#TrainingSandbox

***
##Summary
This is a collection of Python scripts and modules for training classifiers and making plots. It incorporates wrappers for scikit-learn, XGBoost, etc. Data is handled using Pandas DataFrames or using PyROOT. There are wrapper classes for producing plots with matpotlib and PyROOT. There are also some image processing tools for producing high-level features from pixel data.

####Structure
All of the run scripts are in the base directory. The shared classes and tools are in the "Tools" directory. Input data should be stored in the "Data" directory. Output from the run scripts (plots, tables, CSV files, etc.) is directed to the "Output" directory.

####Example Working Packages and Versions
    matplotlib (1.5.2)
    numpy (1.11.2)
    pandas (0.18.1)
    scikit-learn (0.18.1)
    seaborn (0.7.1)
    tensorflow (0.10.0rc0)
    Theano (0.8.2)
    xgboost (0.4a30)

***
##Git Refresher (for Terminal Work)

####Clone the repository on your local machine:
    git clone https://github.com/jwebste2/TrainingSandbox.git TrainingSandbox

####Basic Pulling:
    git pull

####Basic Pushing:
    # To include changes to files that are already tracked
    git add -u

    # To add new files that are not yet tracked
    git add filenameA filenameB ...

    # Then commit the changes    
    git commit -m "Add a log message"

    # Then push the commit
    git push

####Merging your branch into master
    # Pull updates from master to your branch
    git pull

    # Commit and push your branch updates
    git commit -m "log message"
    git push

    # Switch to the master branch and then merge in your changes from your_branch
    git checkout master
    git pull
    git merge your_branch

    # Go back to editing your branch if you want
    git checkout your_branch
    git rebase master


####Checking Logs:
    # Format ==> git log -NEntriesToPrint, e.g.
    git log -5
