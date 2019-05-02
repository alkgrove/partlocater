# partlocater
Find a part on Digi-Key and import parameters into local database

We are not associated with Digi-Key in any way other than being a long time customer. Digi-Key has an api-portal for which one of the functions is to provide all the technical parameters for the components they sell. They aggressively keep this accurate and up to date as if their business depends on it. This app will query Digi-Key with a Digi-Key partnumber and downloads the parameters from Digi-Key and puts them into a SQL database. Several eCAD tools can use the information in the database to put the information into the schematic. 

I use Altium and was very enthusiastic about their ability to query some popular distributors and place the parameters into the schematic symbol. I wrote all sorts of scripts that would check for errors (correct footprints, correect packaging etc.) Then they bought Octopart and it went weird. Data from the distributor was being changed by Octopart, all my scripts broke. So I wrote this tool. Initially it is written for Altium Designer because that is what I'm using this year. 

It would be cool if this were made to work on open-source tools. Haven't researched that yet though.

This was written in Python and requires Python 3. It interfaces to a MariaDB SQL database and therefore requires the database and connector to that database. Digi-Key uses a restrictive version of OATH2 for authentication. The bottom line is that you need a call back web server running locally to initially get an authorization token (or if the token is corrupt). The tokens after the initial one are updated by the tool itself and you don't need a web server for that. 

Digi-Key has a .net solution if you want a fully windows solution. I've never used it. 
So for local usage, I recommend XAMPP. XAMPP contains apache, php, cURL and MariaDB and installs on Windows. The reason for this is I wanted to be able to scale it to an intranet server and Apache, MareaDB, PHP, and cURL work on most Linux and Unix OS. So in the doc folder is a description on how to set this up. 

Please do not expose this to the internet.  While we made some effort to stop SQL injection it probably will not stop all of them. It was designed for either a single workstation or a group of workstations and an intranet server. 



 
