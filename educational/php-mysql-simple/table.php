<html>
	<?php
		function receive($key, $default)
		{
			if (key_exists($key, $_GET))
				return $_GET[$key];
			if (key_exists($key, $_POST))
				return $_POST[$key];
			return $default;
		}
		$max_x = receive('max_x', 20);
		$max_y = receive('max_y', 10);
		$color = receive('color', '#ffffff');
		$border_color = receive('border_color', '#00AAAA');

		$r = hexdec(substr($color, 1, 2));
		$g = hexdec(substr($color, 3, 2));
		$b = hexdec(substr($color, 5, 2));
		if ($r < 160 && $g < 160 && $b < 160)
			$text_color = '#ffffff';
		else
			$text_color = '#000000';
	?>
	<head>
		<title>где резы фт</title>
		<meta charset="utf-8">
		<style>
			table {
				border-color: <?php echo $border_color; ?>;
			}
		</style>
	</head>
	<body>
		<!-- 
		я обманул вашу систему
		увольняйте кибербеза
		-->
		<h1>теперь давайте php reverse shell делать =)</h1>
		
		<!-- form -->
		<form method="post">
			<table bgcolor="#e2e2e2">
				<tr>
					<td width="100px">
						<label for="max_x">Ширина</label>
					</td>
					<td>
						<input type="number" name="max_x" value="<?php echo $max_x; ?>" />
					</td>
				</tr>
				<tr>
					<td width="100px">
						<label for="max_x">Высота</label>
					</td>
					<td>
						<input type="number" name="max_y" value="<?php echo $max_y; ?>" />
					</td>
				</tr>
				<tr>
					<td width="100px">
						<label for="max_x">Цвет фона</label>
					</td>
					<td>
						<input type="color" name="color" value="<?php echo $color; ?>" />
					</td>
				</tr>
				<tr>
					<td width="100px">
						<label for="max_x">Цвет границ</label>
					</td>
					<td>
						<input type="color" name="border_color" value="<?php echo $border_color; ?>" />
					</td>
				</tr>
				<tr>
					<td width="100px">
						<input type="submit" value="Отправить" />
					</td>
				</tr>
			</table>
		</form>
		
		<!-- result -->
		<table border=1 cellspacing=0 cellpadding=10 bgcolor="<?php echo $color; ?>" style="color: <?php echo $text_color; ?>">
		<?php
			// first line
			echo "<tr>\n  <td></td>\n  ";
			for ($i = 1; $i <= $max_x; $i++)
				echo "<td>" . $i . "</td>";
			echo "</tr>\n";
			
			// all table
			for ($y = 1; $y <= $max_y; $y++)
			{
				echo "<tr>\n  <td>" . $y . "</td>\n  ";
				for ($x = 1; $x <= $max_x; $x++)
					echo "<td>" . $x * $y . "</td>";
				echo "</tr>\n";
			}
		?>
		</table>
	</body>
</html>
