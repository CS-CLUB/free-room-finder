
<form class="form-horizontal">

	<!-- Username label and textbox -->
	<div class="control-group">
		<label class="control-label" for="inputEmail">User name:</label>				
		<div class="controls">
			<input type="text" id="login_username" name="login_username" maxlength="31" pattern="^[A-Za-z][A-Za-z0-9]*(?:_[A-Za-z0-9]+)*$" placeholder="Username">      		
		</div>
	</div>
	
	<!-- Password label and textbox -->
	<div class="control-group">
		<label class="control-label" for="inputPassword">Password</label>
		<div class="controls">
			<input type="password" id="login_password" name="login_password" maxlength="31" pattern="^[a-zA-Z0-9\!\$\%\^\&amp;\*\(\)\_\?]{6,31}$" placeholder="Password">
		</div>
	</div>

	<!-- Remember me label and checkbox -->
	<div class="control-group">
		<div class="controls">
			<label class="checkbox">
				<input type="checkbox" id="login_remember" name="login_remember" checked="checked" value="1" > Remember me
			</label>
			<button type="submit" id="LoginButton" name="LoginButton" class="btn">Sign in</button>
		</div>
	</div>
	
	<!-- 'Not a member...' and register button' -->
	<div class="control-group">
		<div class="controls">

		</div>
	</div>			
		
	
</form>






	




