<?php
/*
 *  Free Room Finder Website
 *
 *
 *  Authors -- Crow's Foot Group
 *  -------------------------------------------------------
 *
 *  Jonathan Gillett
 *  Joseph Heron
 *  Amit Jain
 *  Wesley Unwin
 *  Anthony Jihn
 * 
 *
 *  License
 *  -------------------------------------------------------
 *
 *  Copyright (C) 2012 Crow's Foot Group
 *
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU Affero General Public License as
 *  published by the Free Software Foundation, either version 3 of the
 *  License, or (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU Affero General Public License for more details.
 *
 *  You should have received a copy of the GNU Affero General Public License
 *  along with this program.  If not, see <http://www.gnu.org/licenses/>.
 */

require_once "inc/free_room_auth.php";
require_once "inc/db_interface.php";
require_once "inc/validate.php";
require_once "inc/verify.php";
require_once "inc/utility.php";

session_start();

/* Connect to the database */
$mysqli_conn = new mysqli("localhost", $db_user, $db_pass, $db_name);

/* check connection */
if (mysqli_connect_errno()) {
	printf("Connect failed: %s\n", mysqli_connect_error());
	exit();
}


/* 1. If the user is not logged in or their session is invalid */
if (verify_login_cookie($mysqli_conn, $SESSION_KEY) === false
	&& (!isset($_SESSION['login'])
	|| verify_login_session($mysqli_conn, $_SESSION['login'], $SESSION_KEY) === false))
{
	/* Redirect the user to the login page */
	header('Location: login.php');
}

/* User has a valid login cookie set / has logged into the site with valid account 
 * and the POST data isset */
elseif ((verify_login_cookie($mysqli_conn, $SESSION_KEY)
			|| verify_login_session($mysqli_conn, $_SESSION['login'], $SESSION_KEY))
		&& isset($_POST['select_room'])
		&& isset($_SESSION['date'])
		&& isset($_SESSION['num_people']))
{
	/* FIX, forgot to account for when user has login cookie set but there is no session
	 * data, have to retrieve username from cookie and then set the session data
	*/
	if (verify_login_cookie($mysqli_conn, $SESSION_KEY))
	{
		/* Get the login cookie data */
		$login_cookie = htmlspecialchars($_COOKIE['login']);

		/* Get the username from login cookie data and set session info */
		$username = username_from_session($mysqli_conn, $login_cookie, $SESSION_KEY);
		set_session_data($mysqli_conn, $username, $SESSION_KEY);
	}
}

/* Invalid cookie or session data/etc.. */
else
{
	/* Redirect the user to the login page */
	header('Location: login.php');
}

/* Get the room selected by the user 
 * $room_selected[0] => room
 * $room_selected[1] => starttime
 * $room_selected[2] => endtime
 */
$room_selected = explode(", ", $_POST['select_room']);

$date = $_SESSION['date'];
$num_people = $_SESSION['num_people'];


/* Record the booked room in the database */
add_request_occupied(	$mysqli_conn, 
						$username, 
						$room_selected[0], 
						$room_selected[1], 
						$room_selected[2], 
						$date, 
						$num_people);

/* Display the template for a room that has been successfully booked */
include 'templates/header-user.php';

include 'templates/booked.php';

/* Include the footer */
include 'templates/footer.php';

?>