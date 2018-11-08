import datetime, time, json, math
from random import randint
from uuid import uuid4
from Crypto.Hash import SHA3_256
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect

from .models import Vote, Block, VoteBackup
from .merkle.merkle_tool import MerkleTools

def generate(request):
    """Generate transactions and fill them with valid values."""
    number_of_transactions = settings.N_TRANSACTIONS
    number_of_tx_per_block = settings.N_TX_PER_BLOCK

    # Delete all data from previous demo.
    deleted_old_votes = Vote.objects.all().delete()[0]
    VoteBackup.objects.all().delete()
    print('\nDeleted {} data from previous simulation.\n'.format(deleted_old_votes))
    # Delete all blocks from previous demo.
    deleted_old_blocks = Block.objects.all().delete()[0]
    print("\nDeleted {} blocks from previous simulation.\n".format(deleted_old_blocks))
    
    # Generate transactions.
    time_start = time.time()
    block_no = 1
    for i in range(1, number_of_transactions + 1):
        # generate random, valid values
        v_id = str(uuid4())
        v_cand = _get_vote()
        v_timestamp = _get_timestamp()
        # directly fill the values and the block id for simulation purpose
        new_vote = Vote(id=v_id, vote=v_cand, timestamp=v_timestamp, block_id=block_no)
        new_backup_vote = VoteBackup(id=v_id, vote=v_cand, timestamp=v_timestamp, block_id=block_no)
        # "Broadcast" to two nodes
        new_vote.save()
        new_backup_vote.save()
        print("#{} new vote: {}".format(i, new_vote)) # for sanity
        if i % number_of_tx_per_block == 0:
            block_no += 1
    time_end = time.time()
    print('\nFinished in {} seconds.\n'.format(time_end - time_start))

    # View the generated transactions
    votes = Vote.objects.order_by('-timestamp')[:100] # only shows the last 100, if any
    context = {
        'votes': votes,
    }
    request.session['transactions_done'] = True
    return render(request, 'simulation/generate.html', context)

def seal(request):
    """Seal the transactions generated previously."""
    if request.session.get('transactions_done') is None:
        redirect('welcome:home')
    del request.session['transactions_done']

    # Puzzle requirement: '0' * (n leading zeros)
    puzzle, pcount = settings.PUZZLE, settings.PLENGTH

    # Seal transactions into blocks
    time_start = time.time()
    number_of_blocks = settings.N_BLOCKS
    prev_hash = '0' * 64
    for i in range(1, number_of_blocks + 1):
        block_transactions = Vote.objects.filter(block_id=i).order_by('timestamp')
        root = MerkleTools()
        root.add_leaf([str(tx) for tx in block_transactions], True)
        root.make_tree()
        merkle_h = root.get_merkle_root()
        
        # Try to seal the block and generate valid hash
        nonce = 0
        timestamp = datetime.datetime.now().timestamp()
        while True:
            enc = ("{}{}{}{}".format(prev_hash, merkle_h, nonce, timestamp)).encode('utf-8')
            h = SHA3_256.new(enc).hexdigest()
            if h[:pcount] == puzzle:
                break
            nonce += 1

        # Create the block
        block = Block(id=i, prev_h=prev_hash, merkle_h=merkle_h, h=h, nonce=nonce, timestamp=timestamp)
        block.save()
        print('\nBlock {} is mined\n'.format(i))
        # Set this hash as prev hash
        prev_hash = h

    time_end = time.time()
    print('\nSuccessfully created {} blocks.\n'.format(number_of_blocks))
    print('\nFinished in {} seconds.\n'.format(time_end - time_start))
    return redirect('simulation:blockchain')

def transactions(request):
    """See all transactions that have been contained in blocks."""
    vote_list = Vote.objects.all().order_by('timestamp')
    paginator = Paginator(vote_list, 100, orphans=20, allow_empty_first_page=True)

    page = request.GET.get('page')
    votes = paginator.get_page(page)

    hashes = [SHA3_256.new(str(v).encode('utf-8')).hexdigest() for v in votes]
    
    # This happens if you don't use foreign key
    block_hashes = []
    for i in range(0, len(votes)):
        try:
            b = Block.objects.get(id=votes[i].block_id)
            h = b.h
        except:
            h = 404
        block_hashes.append(h)
    
    # zip the three iters
    votes_pg = votes # for pagination
    votes = zip(votes, hashes, block_hashes)
    
    # Calculate the voting result of 3 cands, the ugly way
    result = []
    for i in range(0, 3):
        try:
            r = Vote.objects.filter(vote=i+1).count()
        except:
            r = 0
        result.append(r)

    context = {
        'votes': votes,
        'result': result,
        'votes_pg': votes_pg,
    }
    return render(request, 'simulation/transactions.html', context)

def blockchain(request):
    """See all mined blocks."""
    blocks = Block.objects.all().order_by('id')
    context = {
        'blocks': blocks,
    }
    return render(request, 'simulation/blockchain.html', context)

def verify(request):
    """Verify transactions in all blocks by re-calculating the merkle root."""
    # Basically, by just creating a session (message) var

    print('verifying data...')
    number_of_blocks = Block.objects.all().count()
    corrupt_block_list = ''
    for i in range(1, number_of_blocks + 1):
        # Select block #i
        b = Block.objects.get(id=i)
        
        # Select all transactions in block #i
        transactions = Vote.objects.filter(block_id=i).order_by('timestamp')

        # Verify them
        root = MerkleTools()
        root.add_leaf([str(tx) for tx in transactions], True)
        root.make_tree()
        merkle_h = root.get_merkle_root()
        
        if b.merkle_h == merkle_h:
            message = 'Block {} verified.'.format(i)
        else:
            message = 'Block {} is TAMPERED'.format(i)
            corrupt_block_list += ' {}'.format(i)
        print('{}'.format(message))
    if len(corrupt_block_list) > 0:
        messages.warning(request, 'The following blocks have corrupted transactions: {}.'.format(corrupt_block_list), extra_tags='bg-danger')
    else:
        messages.info(request, 'All transactions in blocks are intact.', extra_tags='bg-info')
    return redirect('simulation:blockchain')

def sync(request):
    """Restore transactions from honest node."""
    deleted_old_votes = Vote.objects.all().delete()[0]
    print('\nTrying to sync {} transactions with 1 node(s)...\n'.format(deleted_old_votes))
    bk_votes = VoteBackup.objects.all().order_by('timestamp')
    for bk_v in bk_votes:
        vote = Vote(id=bk_v.id, vote=bk_v.vote, timestamp=bk_v.timestamp, block_id=bk_v.block_id)
        vote.save()
    print('\nSync complete.\n')
    messages.info(request, 'All blocks have been synced successfully.')
    return redirect('simulation:blockchain')

def sync_block(request, block_id):
    """Restore transactions of a block from honest node."""
    b = Block.objects.get(id=block_id)
    print('\nSyncing transactions in block {}\n'.format(b.id))
    # Get all existing transactions in this block and delete them
    Vote.objects.filter(block_id=block_id).delete()
    # Then rewrite from backup node
    bak_votes = VoteBackup.objects.filter(block_id=block_id).order_by('timestamp')
    for bv in bak_votes:
        v = Vote(id=bv.id, vote=bv.vote, timestamp=bv.timestamp, block_id=bv.block_id)
        v.save()
    # Just in case, delete transactions without valid block
    block_count = Block.objects.all().count()
    Vote.objects.filter(block_id__gt=block_count).delete()
    Vote.objects.filter(block_id__lt=1).delete()
    print('\nSync complete\n')
    return redirect('simulation:block_detail', block_hash=b.h)

def block_detail(request, block_hash):
    """See the details of a block and its transactions."""
    # Select the block or 404
    block = get_object_or_404(Block, h=block_hash)
    confirmed_by = (Block.objects.all().count() - block.id) + 1
    # Select all corresponding transactions
    transaction_list = Vote.objects.filter(block_id=block.id).order_by('timestamp')
    paginator = Paginator(transaction_list, 100, orphans=20)

    page = request.GET.get('page')
    transactions = paginator.get_page(page)
    transactions_hashes = [SHA3_256.new(str(t).encode('utf-8')).hexdigest() for t in transactions]
    
    # Check the integrity of transactions
    root = MerkleTools()
    root.add_leaf([str(tx) for tx in transaction_list], True)
    root.make_tree()
    merkle_h = root.get_merkle_root()
    tampered = block.merkle_h != merkle_h
    
    transactions_pg = transactions # for pagination
    transactions = zip(transactions, transactions_hashes)
    
    # Get prev and next block id
    prev_block = Block.objects.filter(id=block.id - 1).first()
    next_block = Block.objects.filter(id=block.id + 1).first()

    context = {
        'bk': block,
        'confirmed_by': confirmed_by,
        'transactions': transactions,
        'tampered': tampered,
        'verified_merkle_h': merkle_h,
        'prev_block': prev_block,
        'next_block': next_block,
        'transactions_pg': transactions_pg,
    }

    return render(request, 'simulation/block.html', context)

# HELPER FUNCTIONS
def _get_vote():
    return randint(1, 3)

def _get_timestamp():
    return datetime.datetime.now().timestamp()
