import os
import json
import re
import random
from collections import Counter
import sys



class WordleSolver:

    def __init__(self, strategy = "random"):
        self.vocab = []
        self.guess_vocab = []
        self.solutions = []
        self.solved = False
        
        allowed_strategies = ["wordgram", "random", "bigram", "ngram", "cheat"]
        if strategy not in allowed_strategies:
            print("Unknown strategy, defaulting to wordgram")
            strategy = "wordgram"

        self.strategy = strategy
        
    class Evidence:
        def __init__(self):
            self.invalid = set()
            self.valid = set()

            self.correct_index = {}
            self.wrong_index = {0:set(), 1:set(), 2:set(), 3:set(), 4:set()}
            self.guesses = set()

        def update(self, guess, feedback):
            for i,c in enumerate(feedback):
                if c == 'g':
                    self.valid.add(guess[i])
                    self.correct_index[i] = guess[i]
                elif c == 'y':
                    self.valid.add(guess[i])
                    self.wrong_index[i].add(guess[i])
                elif c == 'b':
                    if guess[i] not in self.valid: #in case of repeated chars that show up as b
                        self.invalid.add(guess[i])
                else:
                    print("Wrong character, assuming b")
                    if guess[i] not in self.valid: #in case of repeated chars that show up as b
                        self.invalid.add(guess[i])

            self.guesses.add(guess)

    """
    Load the json that handles the Wordle dictionaries for doing self-evaluation or running as a solver
    """
    def load_vocab(self):
        print("Loading vocabulary")

        with open('vocab.json') as vocab_file:
            vocab = json.load(vocab_file)
            self.vocab = vocab["solutions"] + vocab["herrings"]

        with open('vocab_freq.json') as vocab_freq_file:
            vocab_freq = json.load(vocab_freq_file)
            self.vocab_frequencies = vocab_freq #for use in unigram frequency strategy

        self.solutions = vocab["solutions"]
        self.guess_vocab = self.vocab

        #some statistics for other guess mechanisms
        self.ngram_frequencies = self.compute_ngram_frequencies()

    """
    Extract ngrams from word
    """
    def ngram(self, word, n):
        return [word[i:i+n] for i in range(len(word)-n+1)]

    """
    Compute ngram frequencies from the vocabulary
    """
    def compute_ngram_frequencies(self):
        bigram_counter = Counter()
        trigram_counter = Counter()
        total_bigrams = 0
        total_trigrams = 0
        for w in self.vocab:
            bigrams = self.ngram(w, 2)
            trigrams = self.ngram(w, 3)
            for ngram in bigrams:
                bigram_counter[ngram] += 1 
                total_bigrams += 1
            for ngram in trigrams:
                trigram_counter[ngram] += 1 
                total_trigrams += 1

        ngram_frequencies = {}
        for ngram in bigram_counter:
            ngram_frequencies[ngram] = bigram_counter[ngram]/total_bigrams


        for ngram in trigram_counter:
            ngram_frequencies[ngram] = trigram_counter[ngram]/total_trigrams

        return ngram_frequencies



    """
    Setup new self play run
    """
    def setup_new_run(self):
        self.solved = False
        self.solution = self.random_pick(self.solutions)
        self.turn = 0
        self.evidence = self.Evidence()
        self.guess_vocab = self.vocab

    def self_play(self):
        
        print ("Playing Turn {0}".format(self.turn))
        if self.turn == 0: # setup game
            self.setup_new_run()
            guess = "adieu"
        else:
            guess = self.build_guess(self.evidence)

        print("Guess: " + guess)
        feedback = self.get_feedback(guess, self.solution)
        print("Feedback:" +  feedback)
        self.evidence.update(guess, feedback)

        if feedback == "ggggg":
            print("Success!")
            self.solved = True
            return
        else:
            self.turn +=1
            self.self_play()

    def validated_input(self, text):
        block = True
        while(block):
            input_str = input(text)
            if len(input_str) != 5:
                print ("Input must be 5 letters!")
            else:
                block = False
        return input_str


    """
    Launch the wordlesolver as a game assistant
    """
    def wordle_play(self):

        if self.turn == 0: # setup game
            self.setup_new_run()

        guess = self.validated_input("What was your guess input? ")

        feedback = self.validated_input("Input wordle feedback using g for green, b for black, and y for yellow: ")
    
        self.evidence.update(guess, feedback)

        if feedback == "ggggg":
            print("You're welcome!")
            return
        elif self.turn > 6:
            print ("You lost right?")
        else:
            print ("Try the following guess")
            print (self.build_guess(self.evidence))
            self.turn +=1
            self.wordle_play()


    def get_feedback(self, guess, solution):

        if(guess == solution):
            return "ggggg"

        feedback = ""
        for i,c in enumerate(guess):
            #check first do we have anything
            solution_index = solution.find(c)
            if solution_index == -1:
                feedback += "b"
            elif guess[i] == solution[i]:
                feedback += "g"
            else:
                feedback += "y"

        return feedback

    """
    Build set of regex patterns to minimize the search space, based on the collected evidence of allowed letters, invalid letters, and letter positions.
    """
    def build_guess(self, evidence):

        #prune the word list
        if evidence.valid:
            valid_charset = set(evidence.valid)

        if evidence.invalid:
            invalid_charset = set(evidence.invalid)

        #build our matching pattern with the index-character knowledge
        indexed_characters = ""
        for idx in range(5):
            if idx in evidence.correct_index:
                indexed_characters += "[{0}]".format(evidence.correct_index[idx])
            else:
                if evidence.wrong_index[idx]: #list not empty
                    indexed_characters += "[^{0}]".format("".join(evidence.wrong_index[idx]))
                else:
                    indexed_characters += "."

        indexed_pattern = "(?={0})".format(indexed_characters)
        
        guess_space = self.guess_vocab

        #remove any words we've already guessed (sometimes the evidence can fit existing guesses)
        if evidence.guesses:
            guess_space = [word for word in guess_space if word not in evidence.guesses ]

        #prune our vocab with all the letters that must be included
        if evidence.valid:
            guess_space = [word for word in guess_space if set(word).issuperset(valid_charset) ]

        #prune our vocab from letters that must be excluded
        if evidence.invalid:
            guess_space = [word for word in guess_space if set(word).isdisjoint(invalid_charset) ]

        #print (guess_space)
        #try to match our vocab to our current evidence
        #print(indexed_pattern)
        guess_space = [word for word in guess_space if  re.match(indexed_pattern, word) ]
        
        #print (self.guess_vocab)
        if (len(guess_space)) == 1: # we're done!
            return guess_space[0]
        elif (len(guess_space)) == 0: # we're done?
            raise Exception("Something went wrong! We ran out of guessing vocabulary")
        else: # pick a guess from the list with a strategy
            if self.strategy == "random":
                return self.random_pick(guess_space)
            elif self.strategy == "bigram":
                return self.bigram_weighted_guess(guess_space)
            elif self.strategy == "ngram":
                return self.ngram_weighted_guess(guess_space)
            elif self.strategy == "wordgram":
                return self.unigram_weighted_guess(guess_space)
            elif self.strategy == "cheat":
                return self.cheat(guess_space)



    """
    Just pick a random guess from the list and be done with it
    """
    def random_pick(self, vocab):
        r = random.randint(0, len(vocab)-1)
        return vocab[r]

    """
    Cheat by using only known solutions as guesses
    """
    def cheat(self, vocab):
        solution_guesses = []
        for guess in vocab:
            if guess in self.solutions:
                solution_guesses.append(guess)

        if len(solution_guesses) == 1:
            return solution_guesses[0]
        else:
            return self.random_pick(solution_guesses)

    """
    Using the knowledge of bigram frequencies in our corpus, choose the likeliest guess based on the current frequency information
    """
    def bigram_weighted_guess(self, vocab):
        scored_guesses = {}
        for guess in vocab:
            ngrams = self.ngram(guess, 2)
            score = sum([self.ngram_frequencies[ngram] for ngram in ngrams] ) 
            scored_guesses[guess] = score
        
        max_guess = max(scored_guesses, key=scored_guesses.get)

        return max_guess

    """
    Using the knowledge of ngram frequencies in our corpus, choose the likeliest guess based on the current frequnecy information
    """
    def ngram_weighted_guess(self, vocab):
        scored_guesses = {}
        for guess in vocab:
            ngrams = self.ngram(guess, 2) + self.ngram(guess, 3)
            score = sum([self.ngram_frequencies[ngram] for ngram in ngrams] ) 
            scored_guesses[guess] = score
        
        max_guess = max(scored_guesses, key=scored_guesses.get)

        return max_guess

    """
    Using the attached unigram frequency dictionary, choose the likeliest guess based on the current frequnecy information
    """
    def unigram_weighted_guess(self, vocab):
        scored_guesses = {}
        for guess in vocab:
            scored_guesses[guess] = self.vocab_frequencies[guess]
        
        max_guess = max(scored_guesses, key=scored_guesses.get)

        return max_guess



if __name__ == "__main__":  

    strategy = "wordgram"

    if len(sys.argv) == 1:
        print ("No args detected, running wordle mode")
        solver = WordleSolver(strategy)
        solver.load_vocab()

        solver.setup_new_run()
        solver.wordle_play()

    if len(sys.argv) >= 2:

        if len(sys.argv) >= 3:
            strategy = sys.argv[2]
    
        if sys.argv[1] == "-wordle" or sys.argv[1] == "-w":
            solver = WordleSolver(strategy)
            solver.load_vocab()

            solver.setup_new_run()
            solver.wordle_play()

        elif sys.argv[1] == "-self" or sys.argv[1] == "-s":
            print ("Running Algorithm self evaluation")

            solver = WordleSolver(strategy)
            solver.load_vocab()
            win = 0
            total = 0
            guess_count = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0}
            for i in range(100):
                print (" New Run! ")
                solver.setup_new_run()
                solver.self_play()
                if solver.turn < 7:
                    win += 1
                    guess_count[solver.turn] += 1
                total += 1

            print ( str(win) + "/" + str(total))
            print (guess_count)

        elif sys.argv[1] == "-h" or sys.argv[1] == "-help":
            print ("-w or -wordle to help solve wordle, -s or -self for evaluating algorithm playing by itself")
            print ("Specify a strategy for your experimentation by adding a followup arg: wordgram, bigram, ngram, or random")

        else:
            print ("No args detected, running wordle mode")
            solver = WordleSolver()
            solver.load_vocab()

            solver.setup_new_run()
            solver.wordle_play()



