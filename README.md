# README

### This is a mackinac island renting website created using only python, html, and bootstrap for my final project.

 #### **Python modules I used:**
  - ***Flask*** and ***flask_login*** for backend stuff
  - ***werkzeug.utils***  for image upload
  - ***sys***  and ***os***  to save image into disk
  - ***sqlite3***  for database
  - ***bcrypt***  for hashing password
  - ***datetime***  for date



#### Some info before running it:
- There is two version, one without the database and another with it.\
The idea is that I have setup the database for the bike rental so you can jump straight in and test it without putting in your own bikes.\
Look below for the step to run either version.

- Another thing to note is that is when you in the login/sign up/checkout page, and you input in invalid information,
the whole page will reload to do the check. The reason for this is because I didn't use any javascript so the page isn't dynamic.

- lastly, some things I **didn't fix** or didn't do due to poor time management/time restraint:
  - **[IMPORTANT]** don't insert the same image with the same name twice, or it will break the system 
  - you can't edit after creating a listing in the admin page, there only delete.
  - there no bootstrap in the admin page and no way to get to admin page without pasting the /admin into the url.
  - unable to create multiple admin accounts.
- thoughts I had when making this projects
  - The return rented bike page is a bad idea, it should be handled by an admin account for when a customer return the bike not by the customer.
  - adding javascript would have been a better idea so the pages won't keep reloading when submitting a form.
  - should have made a docker container (was too lazy to change bios setting on my pc to make docker work...)

### Empty Database:
make sure you are in the `Mackinac-Island-Bike-Rental-Website` folder where the `requirements.txt` file is at.
Next, open the terminal in said folder and run the command:
```shell
pip install -r requirements.txt
python ./src/main.py
```
**Note:** 
the first account you create will be the admin account i.e. have access to admin webpage.\
Any account created after will have customer account.\
To access admin page, login to admin account and do http://127.0.0.1:5000/admin or http://localhost:5000/admin \
[this is the only way to access the admin page]

I also included some bike images for you to test out when creating a listing in the admin page.\
Just don't use the same image name twice

### Preset Database:
make sure you are in the `Mackinac-Island-Bike-Rental-Website` folder where the `requirements.txt` file is at.
Next, open the terminal in said folder and run the command:
```shell
pip install -r requirements.txt
python ./src/main.py
```
**Note:** 
To access the admin page, log in using username: `andy` password:`1234` and do http://127.0.0.1:5000/admin or http://localhost:5000/admin \
[this is the only way to access the admin page]\
There is also a customer account using the login username: `andy1` password: `1234`\
[This database preset already include 3 bikes that the customer can rent]




# Issues
if you have bcrypt issue do
```shell
pip uninstall bcrypt
pip uninstall python-bcrypt
```
```shell
pip install bcrypt
```
https://stackoverflow.com/questions/30456762/typeerror-hashpw-argument-1-must-be-str-not-bytes-when-trying-to-register