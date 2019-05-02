<html>
<head>
<title>Digikey API Authorization</title>
</head>
<body><div style="height: 512px;background-color: white;background-image: linear-gradient(white, lightgrey)">
<?php
// Location of the configuration file used by partlocater
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
$ini = parse_ini_file($configfile, true);
$auth = $ini['authentication'];
$client_id = $auth['client_id'];
$redirect_uri =  $auth['redirect_uri'];
if (strlen($client_id) < 28) {
printError("partlocater.cfg doesn't look like it is set up properly");
}
$query = "https://sso.digikey.com/as/authorization.oauth2?response_type=code&client_id=" . $client_id . "&redirect_uri=" . $redirect_uri;
echo "<h4 style=\"color:black\">Digi-Key Initial Authentication Link</h4>";
echo "<div style=\"font-weight:bold;\">";
echo "<A href=\"" . $query . "\">" . $query . "</A></div><br>";
echo "<div style=\"color:black\">Click on the above link to get initial token from Digi-Key</div>";
}
?>
</div>
</body>
</html>
