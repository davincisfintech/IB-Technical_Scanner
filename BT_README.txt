***  Installation ***

install python 3.10/11 for your operating system using this link  https://www.python.org/downloads/

install pycharm community edition using this link  https://www.jetbrains.com/pycharm/download/


*** Setup  ***

run following commands from command prompt/terminal

for MacOs/Linux:
      cd < project directory>           # move to project directory
      python -m venv venv              # create virtual environment
      source venv/bin/activate         # activate virtual environment
      pip install -r requirements.txt    # install dependencies

for windows:
       cd < project directory>           # move to project directory
       python -m venv venv              # create virtual environment
       venv\Scripts\activate            # activate virtual environment
       pip install -r requirements.txt     # install dependencies


*** Parameters ***

provide parameters in back_test.py file as specified in it


*** How To Run ***

Option 1:
    To run using pycharm:

    set back_test.py located in main folder in pycharm configuration and click on run button to run program

Option 2:
    To run using terminal:

    run following commands from command prompt/terminal

    for MacOs/Linux:
          cd < project directory>           # move to project directory
          source venv/bin/activate         # activate virtual environment
          python back_test.py   # Run program

    for windows:
           cd < project directory>           # move to project directory
           venv\Scripts\activate            # activate virtual environment
           back_test.py           # Run program

Option 3:
    for windows OS only:
    double click back_test.bat file


*** Output file ***
output excel file containing back test results will get created inside records folder with name specified in
parameters output file name will be {name_specified}_{time_of_day}.xlsx


*** logs ***

Each run will create date wise log files inside logs folder showing all details of backtest