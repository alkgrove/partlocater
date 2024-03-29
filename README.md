# partlocater
Find a part on Digi-Key and import parameters into local database
*We are now compatible with Digi-Key V3 API*
We are not associated with Digi-Key in any way other than being a long time customer. Digi-Key has an api-portal for which one of the functions is to provide all the technical parameters for the components they sell. They aggressively keep this accurate and up to date as if their business depends on it. This app will query Digi-Key with a Digi-Key partnumber and downloads the parameters from Digi-Key and puts them into a SQL database. Several eCAD tools can use the information in the database to put the information into the schematic. 

This could work for a number of tools such as Orcad and Altium. Since I have Altium, it is the first tool that it works for. 

It would be cool if this were made to work on open-source tools. Haven't researched that yet though.

This was written in Python and requires Python 3. It interfaces to a MariaDB SQL database and therefore requires the database and connector to that database. Digi-Key uses a restrictive version of OATH2 for authentication. The bottom line is that you need a call back web server running locally to initially get an authorization token (or if the token is corrupt). The tokens after the initial one are updated by the tool itself and you don't need a web server for that. 

Digi-Key has a .net solution if you want a fully windows solution. I've never used it. 
So for local usage, I recommend XAMPP. XAMPP contains apache, php, cURL and MariaDB and installs on Windows. The reason for this is I wanted to be able to scale it to an intranet server and Apache, MareaDB, PHP, and cURL work on most Linux and Unix OS. So in the doc folder is a description on how to set this up. 

This was intended to work for either single engineer or a small group. It can work from a single workstation or to a local server. 
 ## v3.0.1
 Added a dialog box for table creation. Digikey has been changing the categories which I used for table generation. I've got a means to map them to a smaller set of tables in the assets/map.cfg file under the Library section. I added a dialog box if a table is going to be created that asked if you want to create a new table or abort. Aborting means you can copy the Category property that triggered the alert and paste it into the assets/map.cfg file as <Category>=<Your Favorite Table>. Restart partlocator and query digikey for the part again. Committing the part shouldn't trigger the alert. 
  ## v3.0.0 
 Updated to be compatible with Digi-Keys V3 API. V2 and V1 have been suspended and will no longer work. Made changes in the treeview user interface where the right hand cells are edittable and no longer require a separate entry box. 
 ## v1.0.4-beta 
 Added a popup database selector if there is more than one database and errors if there are no databases. If there is one database it will automatically open on startup. 
 
 ## v1.1.0 
 The existing database would fail to load in newer versions of mariadb (10.x). The property tables can have over a hundred columns and for later Mariadb this violated the table size by using varchar types. The solution was to move most types to TEXT. In the assets directory is a simple command line script to change the datatype of an exported .sql database to a newer type. If you are using partlocater for the first time, you do not need to do anything, it will automatically use the right thing. 
 
 Digikey is changing their API and the existing one will be going away. I am converting partlocater over to the new system; owever, this will continue to work. Note that the instructions for getting an account in the partlocater documentation will no longer work. The biggest difference is that you use the standard digikey login rather than having to sign up for the API. You go to the developers portal and create an organization and production app to get the client ID and client secret. 

## v1.5.0
partlocater uses tkinter and the treeview is dated and did not have editable cells. I found an idea on the web to make that work and implemented it for the parameter list on locate on Digikey plus the search view. Made other minor changes to the UI. A new revieion is coming to accomadate the v3 API for Digikey as they are depracating v2. Wanted to get the UI changes out first. 
This has been tested on Windows 7 and 10. 
