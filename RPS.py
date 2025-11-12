import random

def player(prev_play, opponent_history=[], my_history=[], seq_counts={}, total_counts={'R':0,'P':0,'S':0}):
    def beats(move):
        return {'R':'P', 'P':'S', 'S':'R'}[move]
    # record opponent move
    if prev_play in ('R','P','S'):
        for k in range(1,5):
            if len(opponent_history) >= k:
                seq = tuple(opponent_history[-k:])
                key = (k, seq)
                if key not in seq_counts:
                    seq_counts[key] = {'R':0,'P':0,'S':0}
                seq_counts[key][prev_play] += 1
        opponent_history.append(prev_play)
        total_counts[prev_play] += 1
    # first move
    if not opponent_history:
        move = random.choice(['R','P','S'])
        my_history.append(move)
        return move
    votes = {'R':0.0,'P':0.0,'S':0.0}
    # n-gram predictor
    for k in range(4,0,-1):
        if len(opponent_history) >= k:
            seq = tuple(opponent_history[-k:])
            key = (k, seq)
            if key in seq_counts:
                counts = seq_counts[key]
                predicted = max(['R','P','S'], key=lambda m: (counts[m], random.random()*1e-6))
                votes[predicted] += 3*(k)
                break
    # frequency predictor
    most_common = max(('R','P','S'), key=lambda m: total_counts[m])
    votes[most_common] += 2.0
    # copy/anticopy detection
    copy_count = anticopy_count = 0
    comp_len = min(len(opponent_history), len(my_history))
    for i in range(comp_len):
        if i >= 1:
            if opponent_history[i] == my_history[i-1]:
                copy_count += 1
            if opponent_history[i] == beats(my_history[i-1]):
                anticopy_count += 1
    if comp_len >= 4:
        denom = comp_len-1
        copy_rate = copy_count/denom if denom>0 else 0
        anticopy_rate = anticopy_count/denom if denom>0 else 0
        if copy_rate > 0.6:
            votes[my_history[-1]] += 3.5
        elif anticopy_rate > 0.6:
            votes[beats(my_history[-1])] += 3.5
    # cycle detection
    seq = opponent_history
    best_cycle_pred = None
    best_conf = 0.0
    max_period = min(6, len(seq)//2) if len(seq) >= 4 else 0
    for p in range(2, max_period+1):
        matches = total_checks = 0
        for i in range(len(seq)-p):
            total_checks += 1
            if seq[i] == seq[i+p]:
                matches += 1
        conf = matches/total_checks if total_checks>0 else 0
        if conf > best_conf and conf > 0.6:
            idx = len(seq) % p
            cycle = seq[:p]
            best_conf = conf
            best_cycle_pred = cycle[idx]
    if best_cycle_pred is not None:
        votes[best_cycle_pred] += 3.0
    # combine votes
    if sum(votes.values()) == 0:
        predicted = most_common
    else:
        max_vote = max(votes.values())
        top = [m for m,v in votes.items() if v == max_vote]
        predicted = random.choice(top)
    chosen = beats(predicted)
    explore_prob = 0.04 if len(opponent_history) < 50 else 0.01
    if random.random() < explore_prob:
        chosen = random.choice(['R','P','S'])
    my_history.append(chosen)
    return chosen
