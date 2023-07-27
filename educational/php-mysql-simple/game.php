<html>
	<?php
		include("connector.php");
		function loginForm()
		{
			echo '<form method="get">' . "\n";
			echo "<tr>\n";
			echo '  <td width="100px"><label for="username">Имя пользователя</label></td>' . "\n";
			echo '  <td><input type="text" name="username"/></td>' . "\n";
			echo "</tr>\n";
			echo '<tr><td width="100px"><input type="submit" value="Отправить" /></td></tr>' . "\n";
			echo "</form>\n";
		}
		function winOrLose($name, $diff_score)
		{
			$request = "UPDATE vitsan SET score=(score";
			if ($diff_score < 0)
				$request .= '-';
			else
				$request .= '+';
			$request .= strval(abs($diff_score));
			$request .= ') WHERE name = "' . $name .'"';
			SqlReq($request);
		}
	?>
	<head>
		<title>вашей империи конец</title>
		<meta charset="utf-8">
		<script>
			if (window.history.replaceState) {
				window.history.replaceState(null, null, window.location.href);
			}
		</script>
	</head>
	<body>
		<h1>pentagon database</h1>
		<table bgcolor="#e2e2e2" border=1 cellspacing=0 cellpadding=10>
		<?php
			if (key_exists('username', $_GET))
			{
				if (key_exists('win', $_POST))
					winOrLose($_GET['username'], 20);
				if (key_exists('lose', $_POST))
					winOrLose($_GET['username'], -20);

				echo '<p>You are <b>' . $_GET['username'] . "</b></p>\n";
				SqlReq("INSERT INTO vitsan (name, score) VALUES ('" . $_GET['username'] . "', 0) ON DUPLICATE KEY UPDATE score=score");
				$results = SqlReq("SELECT name, score FROM vitsan");
				foreach ($results as $row)
					echo '<tr><td width="100px">' . $row['name'] . '</td><td>' . $row['score'] . "</td></tr>\n";
			}
			else
				loginForm();
		?>
		</table>
		<table cellspacing=0 cellpadding=10>
		<?php
			if (key_exists('username', $_GET))
				echo '<form method="post"><tr><td width="100px"><input type="submit" name="win" value="Выиграл" /></td><td width="100px"><input type="submit" name="lose" value="Проиграл" /></td></tr></form>';
		?>
	</body>
	<?php SqlClose(); ?>
</html>
