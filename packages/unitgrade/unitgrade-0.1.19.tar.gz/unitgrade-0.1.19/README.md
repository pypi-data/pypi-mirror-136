
# Unitgrade

Unitgrade is an automatic report and exam evaluation framework that enables instructors to offer automatically evaluated programming assignments. 
 Unitgrade is build on pythons `unittest` framework so that the tests can be specified in a familiar syntax and will integrate with any modern IDE. What it offers beyond `unittest` is the ability to collect tests in reports (for automatic evaluation) and an easy and 100% safe mechanism for verifying the students results and creating additional, hidden tests. A powerful cache system allows instructors to automatically create test-answers based on a working solution. 

 - 100% Python `unittest` compatible
 - No external configuration files, just write a `unittest`
 - No unnatural limitations: If you can `unittest` it, it works.   
 - Granular security model: 
    - Students get public `unittests` for easy development of solutions
    - Students get a tamper-resistant file to create submissions which are uploaded
    - Instructors can automatically verify the students solution using Docker VM and by running hidden tests
    - Allow export of assignments to Autolab (no `make` file mysteries!)
 - Tests are quick to run and will integrate with your IDE

## Installation
Unitgrade can be installed using `pip`:
```
pip install unitgrade
```
This will install unitgrade in your site-packages directory. If you want to upgrade an old installation of unitgrade:
```
pip install unitgrade --upgrade
```
If you are using anaconda+virtual environment you can install it as
```
source activate myenv
conda install git pip
pip install unitgrade
```

When you are done, you should be able to import unitgrade:
```
import unitgrade
```

## Evaluating a report
Homework is broken down into **reports**. A report is a collection of questions which are individually scored, and each question may in turn involve multiple tests. Each report is therefore given an overall score based on a weighted average of how many tests are passed.
In practice, a report consist of an ordinary python file which they simply run. It looks like this (to run this on your local machine, follow the instructions in the previous section):
```
python cs101report1.py
```
The file `cs101report1.py` is just an ordinary, non-obfuscated file which they can navigate and debug using a debugger. The file may contain the homework, or it may call functions the students have written.  Running the file creates console output which tells the students their current score for each test:

```terminal
 _   _       _ _   _____               _      
| | | |     (_) | |  __ \             | |     
| | | |_ __  _| |_| |  \/_ __ __ _  __| | ___ 
| | | | '_ \| | __| | __| '__/ _` |/ _` |/ _ \
| |_| | | | | | |_| |_\ \ | | (_| | (_| |  __/
 \___/|_| |_|_|\__|\____/_|  \__,_|\__,_|\___| v0.0.3, started: 07/09/2021 00:42:25

Week 4: Looping (use --help for options)
Question 1: Test the cluster analysis method                                                                            
 * q1.1) clusterAnalysis([0.8, 0.0, 0.6]) = [1, 2, 1] ?.............................................................PASS
 * q1.2) clusterAnalysis([0.5, 0.6, 0.3, 0.3]) = [2, 2, 1, 1] ?.....................................................PASS
 * q1.3) clusterAnalysis([0.2, 0.7, 0.3, 0.5, 0.0]) = [1, 2, 1, 2, 1] ?.............................................PASS
 * q1.4) Cluster analysis for tied lists............................................................................PASS
 * q1)   Total.................................................................................................... 10/10
 
Question 2: Remove incomplete IDs                                                                                       
 * q2.1) removeId([1.3, 2.2, 2.3, 4.2, 5.1, 3.2,...]) = [2.2, 2.3, 5.1, 3.2, 5.3, 3.3,...] ?........................PASS
 * q2.2) removeId([1.1, 1.2, 1.3, 2.1, 2.2, 2.3]) = [1.1, 1.2, 1.3, 2.1, 2.2, 2.3] ?................................PASS
 * q2.3) removeId([5.1, 5.2, 4.1, 4.3, 4.2, 8.1,...]) = [4.1, 4.3, 4.2, 8.1, 8.2, 8.3] ?............................PASS
 * q2.4) removeId([1.1, 1.3, 2.1, 2.2, 3.1, 3.3,...]) = [4.1, 4.2, 4.3] ?...........................................PASS
 * q2.5) removeId([6.1, 3.2, 7.2, 4.2, 6.2, 9.1,...]) = [9.1, 5.2, 1.2, 5.1, 1.2, 9.2,...] ?........................PASS
 * q2)   Total.................................................................................................... 10/10
 
Question 3: Bacteria growth rates                                                                                       
 * q3.1) bacteriaGrowth(100, 0.4, 1000, 500) = 7 ?..................................................................PASS
 * q3.2) bacteriaGrowth(10, 0.4, 1000, 500) = 14 ?..................................................................PASS
 * q3.3) bacteriaGrowth(100, 1.4, 1000, 500) = 3 ?..................................................................PASS
 * q3.4) bacteriaGrowth(100, 0.0004, 1000, 500) = 5494 ?............................................................PASS
 * q3.5) bacteriaGrowth(100, 0.4, 1000, 99) = 0 ?...................................................................PASS
 * q3)   Total.................................................................................................... 10/10
 
Question 4: Test the fermentation rate question                                                                         
 * q4.1) fermentationRate([20.1, 19.3, 1.1, 18.2, 19.7, ...], 15, 25) = 19.600 ?....................................PASS
 * q4.2) fermentationRate([20.1, 19.3, 1.1, 18.2, 19.7, ...], 1, 200) = 29.975 ?....................................PASS
 * q4.3) fermentationRate([1.75], 1, 2) = 1.750 ?...................................................................PASS
 * q4.4) fermentationRate([20.1, 19.3, 1.1, 18.2, 19.7, ...], 18.2, 20) = 19.500 ?..................................PASS
 * q4)   Total.................................................................................................... 10/10
 
Total points at 00:42:25 (0 minutes, 0 seconds)....................................................................40/40
Provisional evaluation
---------  -----
q1) Total  10/10
q2) Total  10/10
q3) Total  10/10
q4) Total  10/10
Total      40/40
---------  -----
 
Note your results have not yet been registered. 
To register your results, please run the file:
>>> report1intro_grade.py
In the same manner as you ran this file.

```
Once you are happy with the result run the script with the `_grade.py`-postfix, in this case `cs101report1_grade.py`:

```
python cs101report1_grade.py
```
This runs the same tests, and generates a file `Report0_handin_18_of_18.token`. The file name indicates how many points you got. Upload this file to campusnet (and no other). 

## Running the tests in pycharm
Naturally, you can also run the tests in pycharm, and this offers you a lot of cool features such as integration with the debugger and the ability to see which tests have failed.
To do this, simply right-click on the `report.py`-file and select `Run as unittest` (or alternatively, `debug as unittest`). This will take you to a screen such as shown below:

![Using unittests in pycharm](https://gitlab.compute.dtu.dk/tuhe/unitgrade/-/raw/master/docs/pycharm.png)

You can see all tests are green indicating they all pass. If you click on a test you can see the console output it generates and you can 
right-click on the tests to re-run individual tests. 


### Why are there two scripts?
The reason why we use a standard test script, and one with the `_grade.py` extension, is because the tests should both be easy to debug, but at the same time we have to prevent accidential changes to the test scripts. Hence, we include two versions of the tests.

# FAQ
 - **My non-grade script and the `_grade.py` script gives different number of points**
Since the two scripts should contain the same code, the reason is nearly certainly that you have made an (accidental) change to the test scripts. Please ensure both scripts are up-to-date and if the problem persists, try to get support.
   
 - **Why is there a `unitgrade` directory with a bunch of pickle files? Should I also upload them?**
No. The file contains the pre-computed test results your code is compared against. If you want to load this file manually, the unitgrade package contains helpful functions for doing so.
   
 - **I am worried you might think I cheated because I opened the '_grade.py' script/token file**
This should not be a concern. Both files are in a binary format (i.e., if you open them in a text editor they look like garbage), which means that if you make an accidential change, they will with all probability simply fail to work. 
   
 - **I think I might have edited the `report1.py` file. Is this a problem since one of the tests have now been altered?**
Feel free to edit/break this file as much as you like if it helps you work out the correct solution. In fact, I recommend you just run `report1.py` from your IDE and use the debugger to work out the current state of your program. However, since the `report1_grade.py` script contains a seperate version of the tests, please ensure your `report1.py` file is up to date.
   
### Debugging your code/making the tests pass
The course material should contain information about the intended function of the scripts used in the tests, and the file `report1.py` should mainly be used to check which of your code is being run. In other words, first make sure your code solves the exercises, and only later run the test script which is less easy/nice to read. 
However, obivously you might get to a situation where your code seems to work, but a test fails. In that case, it is worth looking into the code in `report1.py` to work out what is going on. 

 - **I am 99% sure my code is correct, but the test still fails. Why is that?**
The testing framework offers a great deal of flexibility in terms of what is compared. This is either: (i) The value a function returns, (ii) what the code print to the console (iii) something derived from these.
   Since the test *might* compare the console output, i.e. what you generate using `print("...")`-statements, innnocent changes to the script, like an extra print statement, can cause the test to fail, which is counter-intuitive. For this reason, please look at the error message carefully (or the code in `report1.py`) to understand what is being compared. 
   
One possibility that might trick some is that if the test compares a value computed by your code, the datatype of that value is important. For instance, a `list` is not the same as a python `ndarray`, and a `tuple` is different from a `list`. This is the correct behavior of a test: These things are not alike and correct code should not confuse them. 

 - **The `report1.py` class is really confusing. I can see the code it runs on my computer, but not the expected output. Why is it like this?**
To make sure the desired output of the tests is always up to date, the tests are computed from a working version of the code and loaded from the disk rather than being hard-coded.

 - **How do I see the output of my programs in the tests? Or the intended output?**
There are a number of console options available to help you figure out what your program should output and what it currently outputs. They can be found using:
 ```python report1.py --help```
Note these are disabled for the `report1_grade.py` script to avoid confusion. It is not recommended you use the grade script to debug your code.  

 - **How do I see the output generated by my scripts in the IDE?**
The file `unitgrade/unitgrade.py` contains all relevant information. Look at the `QItem` class and the function `get_points`, which is the function that strings together all the tests. 

 - **Since I cannot read the `.token` file, can I trust it contains the same number of points internally as the file name indicate?**
Yes. 

### Privacy/security   
 - **I managed to reverse engineer the `report1_grade.py`/`*.token` files in about 30 minutes. If the safety measures are so easily broken, how do you ensure people do not cheat?**
That the script `report1_grade.py` is difficult to read is not the principle safety measure. Instead, it ensures there is no accidential tampering. If you muck around with these files and upload the result, we will very likely know.     

- **I have private data on my computer. Will this be read or uploaded?**
No. The code will look for and upload your solutions, but it will not read/look at other directories in your computer. In the example provided with this code, this means you should expect unitgrade to read/run all files in the `cs101courseware_example`-directory, but **no** other files on your computer. So as long as you keep your private files out of the base courseware directory, you should be fine. 

- **Does this code install any spyware/etc.? Does it communicate with a website/online service?**
No. Unitgrade makes no changes outside the courseware directory and it does not do anything tricky. It reads/runs code and write the `.token` file.
  
- **I still have concerns about running code on my computer I cannot easily read**
Please contact me and we can discuss your specific concerns.
  

# Citing
```bibtex
@online{unitgrade,
	title={Unitgrade (0.0.3): \texttt{pip install unitgrade}},
	url={https://lab.compute.dtu.dk/tuhe/unitgrade},
	urldate = {2021-09-07}, 
	month={9},
	publisher={Technical University of Denmark (DTU)},
	author={Tue Herlau},
	year={2021},
}
```