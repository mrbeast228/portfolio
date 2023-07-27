<?php
$link = @mysqli_connect('localhost', 'root', '', 'bebra228');
if ($err = @mysqli_connect_errno())
	die("Ошбка подключения:" . $err . "");

function SqlReq($query)
{
	$res = @mysqli_query($GLOBALS['link'], $query) or die(mysqli_error($GLOBALS['link']));
	$a = [];
	while ($row = @mysqli_fetch_array($res))
		$a[] = $row;
	return $a;
}

function SqlClose()
{
	mysqli_close($GLOBALS['link']);
}
?>
