<html>
<head>
<title>Digikey Authentication</title>
</head>
<body><div style="height: 512px;background-color: white;background-image: linear-gradient(white, lightgrey)">
<?php
$configfile=getenv("PARTLOCATER_CFG");
function printError($errorString)
{
	echo "<h2 style=\"color:red\">Error</h2>";
	echo "<div style=\"font-weight:bold;font-size:larger\">" . $errorString . "</div>";
}

if ($configfile == false) {
printError("Environment Variable PARTLOCATER_CFG is not set");
} elseif (!file_exists($configfile)) {
printError("partlocater.cfg file not found");
} else {
// to do call parse_ini_file($configfile, true) which 
// creates an associative array of sections. 
// this way, you can select which database gets the token
$ini = parse_ini_file($configfile, true);
$auth = $ini['authentication'];
date_default_timezone_set($auth['timezone']);
$authdata = array('code' => $_GET['code'],
	'client_id' => $auth['client_id'],
	'client_secret' => $auth['client_secret'],
	'redirect_uri' => $auth['redirect_uri'],
	'grant_type' => 'authorization_code');
$authurl = curl_init();
curl_setopt($authurl, CURLOPT_URL, 'https://sso.digikey.com/as/token.oauth2');
curl_setopt($authurl, CURLOPT_RETURNTRANSFER, true);
curl_setopt($authurl, CURLOPT_POSTFIELDS, http_build_query($authdata));
curl_setopt($authurl, CURLOPT_POST, true);
$headers = array();
$headers[] = 'Content-Type: application/x-www-form-urlencoded';
curl_setopt($authurl, CURLOPT_HTTPHEADER, $headers);
$result = curl_exec($authurl);
if (curl_errno($authurl)) {
    printError('Unable to contact authentication site: ' . curl_error($authurl));
    exit;
}
curl_close ($authurl);
$token=json_decode($result, true);
$err = json_last_error();
if ($err != 0) {
   printError('Invalid JSON received (json error ' . $err . ')');
   exit;
}
if (array_key_exists('error_description',$token)) {
   printError('Invalid Grant ' . $token['error_description']);
   exit;
}
$pref = $ini['preferences'];
if (!array_key_exists('default', $pref)) {
	printError('There is no preference default database defined in partlocater.cfg.');
	exit;
}
if (!array_key_exists($pref['default'], $ini)) {
	printError('database section ' . $pref['default'] . ' not found in partlocater.cfg.');
	exit;
}
$defdb = $ini[$pref['default']];
$host = $defdb['host'];
$user = $defdb['username'];
$pass = $defdb['password'];
$dbname = $defdb['database'];

$db = mysqli_connect($host, $user, $pass,null,'3306');
if (mysqli_connect_error()) {
	printError('Unable to connect to database ' . mysqli_connect_error());
	exit;
}
$timestamp = date('Y-m-d G:i:s');
$metadbname = $dbname . "_metadata";
$use_db = mysqli_select_db($db, $metadbname);
if (!$use_db) {
	$query_str = "CREATE DATABASE `" . $metadbname ."`;";
	if (!mysqli_query($db,$query_str)) {
		printError('Unable to create database ' . $metadbname);
		exit;
	}
	$query_str = "CREATE TABLE IF NOT EXISTS `". $metadbname. "`.`Token` (
		`access_token` VARCHAR(255) DEFAULT NULL, `refresh_token` VARCHAR(255) DEFAULT NULL,
		`token_type` VARCHAR(255) DEFAULT NULL, `expires_in` VARCHAR(255) DEFAULT NULL, 
		`timestamp` TIMESTAMP NULL DEFAULT NULL);";
	if (!mysqli_query($db,$query_str)) {
		printError('Unable to create token table for ' . $metadbname);
		exit;
	}
		
}
$query_str = "INSERT INTO `". $metadbname . "`.`Token` (`access_token`, `refresh_token`, `token_type`, `expires_in`, `timestamp`) VALUES ('". $token['access_token']."','".$token['refresh_token']."','".$token['token_type']."','".$token['expires_in']."','".$timestamp."');";

if (!mysqli_query($db,$query_str)) {
	printError('Data base query failed ' . $query_str);
	exit;
}

$use_db = mysqli_select_db($db, $dbname);
if (!$use_db) {
	$query_str = "CREATE DATABASE `" . $dbname ."`;";
	if (!mysqli_query($db,$query_str)) {
		printError('Unable to create database ' . $dbname);
		exit;
	}
}
mysqli_close($db);
echo "<h2 style=\"color:black\">Success</h2>";
echo "<div style=\"font-weight:bold;font-size:larger\">Database updated with new Token (" .$token['access_token'] . ")</div>";
echo "<div style=\"font-weight:bold;font-size:larger\"> " . $timestamp . "</div>";
}
?>
</div>
</body>
</html>
