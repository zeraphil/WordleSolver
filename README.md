### Yet Another Wordle Solver

Wordle Solver without additional dependencies, just pull and run.

-s will play 100 games by itself for algorithm evaluation

-w or -wordle will assist you in running the game. Note that feedback must be provided with g, b, y, where g is green, b is black or no hit, and y is yellow.

The algorithm uses the expected set logic for pruning the search space, plus an indexed regex match string. For choosing guesses, I implemented a couple of strategies, the obvious random pick, and also computed the bi/tri gram frequencies of the corpus to try to effectively choose the guess that captures the likeliest character relationships in the word list. 

This is done completely naive, meaning I don't treat solutions vs additional words  (in the Wordle source, termed solutions and herrings) any differently, they are aggregated before any processing happens. 

