### Yet Another Wordle Solver

Wordle Solver without additional dependencies, just pull and run.

-s will play 100 games by itself for algorithm evaluation

-w or -wordle will assist you in running the game. Note that feedback must be provided with g, b, y, where g is green, b is black or no hit, and y is yellow.

The algorithm uses the expected set logic for pruning the search space, plus an indexed regex match string. For choosing guesses, I implemented a couple of strategies, the obvious random pick, and also computed the bi/tri gram frequencies of the corpus to try to effectively choose the guess that captures the likeliest character relationships in the word list. 

This is done completely naive, meaning I don't treat solutions vs additional words  (in the Wordle source, termed solutions and herrings) any differently, they are aggregated before any processing happens. 

1/17/2022: Added the wordgram strategy, which essentially uses known word counts from wikipedia data sets as weights for selecting guesses, rather than calculating from the known corpus itself. This required loading the vocab_freq file.

 More things could be done to increase performance or winrate but I feel this is close to emulating a perfect "human game". 
 
 Added also a "cheat" strategy, if you want to always win at wordle, which uses only the known solutions. Since the search function is already optimal, this is adding nearly perfect information and thus, this will result in perfect games nearly 100% of the time, which wasn't the point of this exercise. I say nearly because the first guess will always determine the outcome. There's a few articles on what a best guess is: for self play we use "adieu" but others might be better. 
