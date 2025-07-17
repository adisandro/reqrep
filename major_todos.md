## IMPLEMENTATION TODOS

1. Add temporal operators (+ any missing operators) in the grammar
    - Add in `src\repair\grammar\functions.py`, alongwith corresponding robubstness measurment
    - Possibly, add support for visulaisatino in `src\repair\approach\optimization\utils.py`
2. add support for pre- and post-conditions
    - redefine the requirement representation to, for instance, have a implication at the top level
    - implement the rules that define a valid requirement at the representaiton level (e.g. pre-condition only on inputs, post-condition only on outputs)
    - maybe some inspiration from here: `src\repair\approach\optimization\expressiongenerator.py`
3. Implement desirability functions (as functions over the current candidate requirement and the originial requirement)
    - Waiting for Aren to write what to do in the paper
    - In `src\repair\fitness\desirability.py`
4. Integrate desirability as a separate objective within the GP approach
    - In `src\repair\approach\optimization\optimization.py:OptimizationApproach.repair`
5. Somehow integrate the initial requirement within the GP approach
    - Will likely be sufficient to do this through the desirability fitness

## STRATEGIC TODOS

1. Select the exact correctness fitness function
    - Aren will write this in the paper
    - Aren is currently thinking finding a fitness that is closest to 0, and negative, as a way to fit the trace suite
    - this is WIP
2. Figure out the numeric constants issue
    - currently, there are 2 types of numeric terminals:
        - constants (e.g. 5, 10, 15) that have fixed value throughout the repair, see `src\repair\grammar\terminals.py:GRAMMAR_STATIC_TERMINALS`
        - ephemeral constants, whihc, at each iteration, take a random value within a range, see `src\repair\grammar\terminals.py:GRAMMAR_EPHEMERAL_TERMINALS`
    - Change this to:
        - include the constants originially in the requirement
        - Include constants or ephemerals that are not random, but instead, maybe get closer to optimized values throughout execution
3. Optimize the correctness fitness evaluation
    - maybe integrate some aggregation of the trace suite to avoid checking 
4. Improve sanity check
    - Pending Aren
    - in `src\repair\fitness\sanitycheck.py`
    - currently based on random sampling
    - Integrate some more formal approaches, symbolic analysis, or simplifying the requirements
    - maybe, integrate it as a desirability function



