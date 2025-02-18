#include "main.h"

#define mateTests (int) 100

/**
 * This method updates the numTransMuts and numRespMuts through out the GA process
 * utilizing dynamic methods to increase and decrease the number of mutation being perfomred during a set of mating events
*/

int updateMutSpread(int dmo){
    if (dmo == 1){ // increase number of transition mutations & decrease number of response mutations
        if (numTransMuts <= 50) numTransMuts++;
        if (numRespMuts >= 0) numRespMuts--;
    }
    else if (dmo == 2){ // increase number of response mutations & decrease number of trasnsition mutations
        if (numRespMuts <= 50) numRespMuts++;
        if (numTransMuts >= 0) numTransMuts--;
    }
    else{// alter the variables based on fitness improvment
        double change = populationBestFit - prevBestFitness; // calculate amount of change between previous and current best fitness
        change = change / prevBestFitness;// calculate percentage increase from previous best fitness

        if (dmo == 3){
            if (change == 0){ // if change equlas zero increase explorative ability of the GA
                numRespMuts += 2;
                numTransMuts += 2;
            }
            else if (numRespMuts - 2 > 0 && numTransMuts - 2 > 0){ // if there was a change, decrease the amount of exploration and increase the amount of exploitation
                numRespMuts -= 2;
                numTransMuts -= 2;
            }
        }
        else{
            if (prevBestFitness != populationBestFit) RICounter = 0;// if there is a change in the best fitness value reset counter
            else RICounter++;// else increase reporting interval counter
            if(RICounter != 0){// add the report interval counter to number of mutations performed to increase exploration
                if(numRespMuts + RICounter < 50)numRespMuts += RICounter;
                else numRespMuts = 50;// place a cap on the number of mutations that can be performed
                if(numTransMuts + RICounter < 50)numTransMuts += RICounter;
                else numTransMuts = 50;// place cap on the number of mutations that can be performed
            }else{// reset the number of mutations to allow for exploration of the improvement
                numRespMuts = 2;
                numTransMuts = 2;
            }
        }
        prevBestFitness = populationBestFit; // update the previous best population fitness value
    }
    return 0;
} // updateMutSpread

int matingEvent(bool biggerBetter, int currentGen, ostream &outp) {
    SDA child1a, child2a, child1b, child2b;
    double fit1a, fit2a, fit1b, fit2b;
    bool improvement = false;

    vector<int> idxs = tournSelect(tournSize, biggerBetter);

    child1a.copy(pop[idxs[0]]);
    fit1a = fits[idxs[0]];
    child2a.copy(pop[idxs[1]]);
    fit2a = fits[idxs[1]];
    if (drand48() < crossoverRate) {
        if (crossoverOp == 0) child1a.twoPointCrossover(child2a);
        else if (crossoverOp == 1) child1a.oneStateCrossover(child2a);

        fit1a = fitness(child1a);
        fit2a = fitness(child2a);
        // If there is an improvement...
        if (((fit1a > populationBestFit && BIGGER_BETTER) || (fit2a > populationBestFit && BIGGER_BETTER)) ||
            ((fit1a < populationBestFit && !BIGGER_BETTER) || (fit2a < populationBestFit && !BIGGER_BETTER))) {
            improvement = true;
            outp << "Crossover Improvement during Mating Event " << currentGen << endl;
            if (BIGGER_BETTER) {
                outp << populationBestFit << " -> " << max(fit1a, fit2a) << endl;
            } else {
                outp << populationBestFit << " -> " << min(fit1a, fit2a) << endl;
            }
            outp << "Parent 1: " << fits[idxs[0]] << endl;
            pop[idxs[0]].printSDA(outp);
            outp << "Parent 2: " << fits[idxs[1]] << endl;
            pop[idxs[1]].printSDA(outp);
            outp << "Child 1: " << fit1a << endl;
            child1a.printSDA(outp);
            outp << "Child 2: " << fit2a << endl;
            child2a.printSDA(outp);

            if (BIGGER_BETTER) {
                populationBestFit = max(fit1a, fit2a);
            } else {
                populationBestFit = min(fit1a, fit2a);
            }
        }
    }

    child1b.copy(child1a);
    fit1b = fit1a;
    child2b.copy(child2a);
    fit2b = fit2a;

    if (drand48() < mutationRate) {
        child1b.mutate(numTransMuts, numRespMuts);
        child2b.mutate(numTransMuts, numRespMuts);

        fit1b = fitness(child1b);
        fit2b = fitness(child2b);
        // If there is an improvement...
        if (((fit1b > populationBestFit && BIGGER_BETTER) || (fit2b > populationBestFit && BIGGER_BETTER)) ||
            ((fit1b < populationBestFit && !BIGGER_BETTER) || (fit2b < populationBestFit && !BIGGER_BETTER))) {
            improvement = true;
            outp << "Mutation Improvement during Mating Event " << currentGen << endl;
            if (BIGGER_BETTER) {
                outp << populationBestFit << " -> " << max(fit1b, fit2b) << endl;
            } else {
                outp << populationBestFit << " -> " << min(fit1b, fit2b) << endl;
            }
            outp << "Child 1 Before: " << fit1a << endl;
            child1a.printSDA(outp);
            outp << "Child 1 After: " << fit1b << endl;
            child1b.printSDA(outp);
            outp << "Child 2 Before: " << fit2a << endl;
            child2a.printSDA(outp);
            outp << "Child 2 After: " << fit2b << endl;
            child2b.printSDA(outp);

            if (BIGGER_BETTER) {
                populationBestFit = max(fit1b, fit2b);
            } else {
                populationBestFit = min(fit1b, fit2b);
            }
        }
    }
    if (improvement){
        if (fit1a > fit1b){
            pop[idxs.end()[-1]] = child1b;
            fits[idxs.end()[-1]] = fit1b;
        } else {
            pop[idxs.end()[-1]] = child1a;
            fits[idxs.end()[-1]] = fit1a;
        }
        if (fit2a > fit2b){
            pop[idxs.end()[-2]] = child2b;
            fits[idxs.end()[-2]] = fit2b;
        } else {
            pop[idxs.end()[-2]] = child2a;
            fits[idxs.end()[-2]] = fit2a;
        }
    } else {
        pop[idxs.end()[-1]] = child1b;
        pop[idxs.end()[-2]] = child2b;

        fits[idxs.end()[-1]] = fit1b;
        fits[idxs.end()[-2]] = fit2b;
    }
    return 0;
}

vector<int> runMultiCross(int numEvents, SDA mom, SDA dad) {
    SDA child1, child2;
    vector<int> fitVals;

    fitVals.reserve(numEvents * 2);

    for (int i = 0; i < numEvents; ++i) {
        child1.copy(mom);
        child2.copy(dad);
        if (crossoverOp == 0) child1.twoPointCrossover(child2);
        else if (crossoverOp == 1) child1.oneStateCrossover(child2);
        fitVals.push_back((int) fitness(child1));
        fitVals.push_back((int) fitness(child2));
    }
    return fitVals;
}

vector<int> runMultiMutate(int numEvents, SDA parent) {
    SDA child;
    vector<int> fitVals;

    fitVals.reserve(numEvents);
    for (int i = 0; i < numEvents; ++i) {
        child.copy(parent);
        child.mutate(numTransMuts, numRespMuts);
        fitVals.push_back((int) fitness(child));
    }
    return fitVals;
}

int crossoverCheck(ofstream &outStream) {
    outStream << "Population Fitness Values:" << endl;

    for (int i = 0; i < popsize; ++i) {
        outStream << fits[i] << endl;
    }

    outStream << "Population Crossover Checks:" << endl;

    for (int mom = 0; mom < popsize; mom++) {
        for (int dad = mom + 1; dad < popsize; dad++) {
            outStream << "Parent Idxs: " << mom << "\t" << dad << endl;
            outStream << "Parent Fits: " << fits[mom] << "\t" << fits[dad] << endl;
            printVector<ofstream, int>(outStream, runMultiCross(mateTests, pop[mom], pop[dad]), "", "\n", true);
        }
    }
    return 0;
}

int mutateCheck(ofstream &outStream) {
    outStream << "Population Fitness Values:" << endl;

    for (int i = 0; i < popsize; ++i) {
        outStream << fits[i] << endl;
    }

    outStream << "Population Mutation Checks:" << endl;

    for (int mom = 0; mom < popsize; mom++) {
        outStream << "Parent Idx: " << mom << endl;
        outStream << "Parent Fit: " << fits[mom] << endl;
        printVector<ofstream, int>(outStream, runMultiMutate(mateTests, pop[mom]), "", "\n", true);
    }
    return 0;
}

int sdaCheck(ofstream &outStream, int currentGen) {
    outStream << "Population After " << currentGen << " Mating Events" << endl;

    for (int sda = 0; sda < popsize; sda++) {
        outStream << "SDA " << sda << endl;
        outStream << "Fitness: " << fits[sda] << endl;
        pop[sda].printSDA(outStream);
        pop[sda].fillOutput(testSeq, true, outStream);
    }
    return 0;
}