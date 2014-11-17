<?php

/**
 * Remote API User Administration configuration
 * 
 * @author 		Author: Raynaldo Rivera 
 */

class API_Server
{
	/**
	 * Defines the service for WSDL
	 *
	 * @var		array
	 */			
	public $__dispatch_map = array();
	
	/**
	 * IPS Global Class
	 *
	 * @var		object
	 */
	protected $registry;
	
	/**
	 * IPS API SERVER Class
	 *
	 * @var		object
	 */
	public $classApiServer;
	
	/**
	 * Constructor
	 * 
	 * @return	@e void
	 */		
	public function __construct( $registry ) 
    {
		//-----------------------------------------
		// Set IPS CLASS
		//-----------------------------------------
		
		$this->registry = $registry;
		
    	//-----------------------------------------
    	// Load allowed methods and build dispatch
		// list
    	//-----------------------------------------
    	$ALLOWED_METHODS = array();
		require_once( DOC_IPS_ROOT_PATH . 'interface/board/modules/aa/methods.php' );/*noLibHook*/
		
		if ( is_array( $ALLOWED_METHODS ) and count( $ALLOWED_METHODS ) )
		{
			foreach( $ALLOWED_METHODS as $_method => $_data )
			{
				$this->__dispatch_map[ $_method ] = $_data;
			}
		}
	}
	
	// Creates a new user
	public function createUser( $api_key, $api_module, $username, $email, $display_name, $md5_passwordHash)
	{
		//-----------------------------------------
		// INIT
		//-----------------------------------------

		$api_key	= IPSText::md5Clean( $api_key );
		$api_module	= IPSText::parseCleanValue( $api_module );
		
		//-----------------------------------------
		// Authenticate
		//-----------------------------------------
		
		if ( $this->__authenticate( $api_key, $api_module, 'createUser' ) !== FALSE )
		{
			
			//-----------------------------------------
			// Add log
			//-----------------------------------------
			$this->addLogging( $api_key );

			//-----------------------------------------
			// Create a user
			//-----------------------------------------
			$test = IPSMember::create( array( 'core' => array( 'email' => $email, 'md5_hash_password' => $md5_passwordHash, 'name' => $username, 'members_display_name' => $display_name) ) );
			
			//-----------------------------------------
			// The way IPSMember::create function works is it can't fail.. It always returns true unless all data isn't provided.
			// However it will still create a partial record. So in essence never fails
			//-----------------------------------------			
			$this->classApiServer->apiSendReply( array('result'   => 'success')	 );
			
			exit();
		}
	}
	
	
	// Deletes a user from the entire system
	public function deleteUser( $api_key, $api_module, $username)
	{
		//-----------------------------------------
		// INIT
		//-----------------------------------------

		$api_key	= IPSText::md5Clean( $api_key );
		$api_module	= IPSText::parseCleanValue( $api_module );
		
		//-----------------------------------------
		// Authenticate
		//-----------------------------------------
		
		if ( $this->__authenticate( $api_key, $api_module, 'deleteUser' ) !== FALSE )
		{
			
			//-----------------------------------------
			// Add log
			//-----------------------------------------
			$this->addLogging( $api_key );

			//-----------------------------------------
			// Remove a user by username
			//-----------------------------------------
			$member = IPSMember::load($username,'all','username');
			
			if ($member != null) {
				$result = IPSMember::remove($member['member_id']);
				
				if($result) {
					$this->classApiServer->apiSendReply( array('result'   => 'success')	 );
				} else {
					$this->classApiServer->apiSendReply( array('result'   => 'failure')	 );
				}
			}

			$this->classApiServer->apiSendReply( array('result'   => 'failure')	 );
			
			exit();
		}
	}
	
	// We disable by just changing the email and password to something random.
	// Allows us to avoid losing post etc.
	public function disableUser( $api_key, $api_module, $username)
	{
		//-----------------------------------------
		// INIT
		//-----------------------------------------

		$api_key	= IPSText::md5Clean( $api_key );
		$api_module	= IPSText::parseCleanValue( $api_module );
		
		//-----------------------------------------
		// Authenticate
		//-----------------------------------------
		
		if ( $this->__authenticate( $api_key, $api_module, 'disableUser' ) !== FALSE )
		{
			
			//-----------------------------------------
			// Add log
			//-----------------------------------------
			$this->addLogging( $api_key );

			//-----------------------------------------
			// Remove a user by username
			//-----------------------------------------
			$member = IPSMember::load($username,'all','username');
			
			if ($member != null) {
			
				$uniqueID = strval(uniqid());
				$uniqueEmail = strval(uniqid());
				$uniqueMD5 = md5($uniqueID);
				$email = $uniqueEmail.'@'.$uniqueEmail.'.com';
				
				$email_result = IPSMember::save( array( 'core' => array( 'field' => 'member_id', 'value' => $member['member_id'])),array('core' => array('email'=>$email)));
				$password_result = $password_result = IPSMember::updatePassword($member['member_id'], $uniqueMD5);
				
				if($email_result && $password_result) {
					$this->classApiServer->apiSendReply( array('result'   => 'success')	 );
				} else {
					$this->classApiServer->apiSendReply( array('result'   => 'failure')	 );
				}
			}

			$this->classApiServer->apiSendReply( array('result'   => 'failure')	 );
			
			exit();
		}
	}
	
	// Used to update the user email, and password.
	// Is also used to re-enable a disabled account
	public function updateUser( $api_key, $api_module, $username, $email, $md5_passwordHash)
	{
		//-----------------------------------------
		// INIT
		//-----------------------------------------

		$api_key	= IPSText::md5Clean( $api_key );
		$api_module	= IPSText::parseCleanValue( $api_module );
		
		//-----------------------------------------
		// Authenticate
		//-----------------------------------------
		
		if ( $this->__authenticate( $api_key, $api_module, 'updateUser' ) !== FALSE )
		{
			
			//-----------------------------------------
			// Add log
			//-----------------------------------------
			$this->addLogging( $api_key );

			//-----------------------------------------
			// Load our user
			//-----------------------------------------
			$member = IPSMember::load($username,'all','username');
			
			if ($member != null) {
				
				$email_result = IPSMember::save( array( 'core' => array( 'field' => 'member_id', 'value' => $member['member_id'])),array('core' => array('email'=>$email)));
				$password_result = $password_result = IPSMember::updatePassword($member['member_id'], $md5_passwordHash);
				
				if($email_result && $password_result) {
					$this->classApiServer->apiSendReply( array('result'   => 'success')	 );
				} else {
					$this->classApiServer->apiSendReply( array('result'   => 'failure')	 );
				}
			}

			$this->classApiServer->apiSendReply( array('result'   => 'failure')	 );
			
			exit();
		}
	}
	
	public function getAllGroups( $api_key, $api_module)
	{
		//-----------------------------------------
		// INIT
		//-----------------------------------------

		$api_key	= IPSText::md5Clean( $api_key );
		$api_module	= IPSText::parseCleanValue( $api_module );
		
		//-----------------------------------------
		// Authenticate
		//-----------------------------------------
		
		if ( $this->__authenticate( $api_key, $api_module, 'getAllGroups' ) !== FALSE )
		{
			
			//-----------------------------------------
			// Add log
			//-----------------------------------------
			$this->addLogging( $api_key );

			//-----------------------------------------
			// Load our user
			//-----------------------------------------
			ipsRegistry::DB()->build(array('select' => 'g_title', 'from' => 'groups'));
			$result = ipsRegistry::DB()->execute();
			$groups = array();
			
			while( $r = ipsRegistry::DB()->fetch($result)) {
				array_push($groups,$r);
			}
			$this->classApiServer->apiSendReply($groups);
			
			exit();
		}
	}
	
	public function getUserGroups( $api_key, $api_module, $username)
	{
		//-----------------------------------------
		// INIT
		//-----------------------------------------

		$api_key	= IPSText::md5Clean( $api_key );
		$api_module	= IPSText::parseCleanValue( $api_module );
		
		//-----------------------------------------
		// Authenticate
		//-----------------------------------------
		
		if ( $this->__authenticate( $api_key, $api_module, 'getUserGroups' ) !== FALSE )
		{
			
			//-----------------------------------------
			// Add log
			//-----------------------------------------
			$this->addLogging( $api_key );
			
			$member = IPSMember::load($username,'all','username');
			$groups = array();
			if( $member['mgroup_others']) {
				$groupids = explode(',' , $member['mgroup_others']);

				foreach ($groupids as &$groupid) {
					ipsRegistry::DB()->build(array('select' => 'g_title', 'from'=>'groups','where'=>'g_id='.$groupid));
					$result = ipsRegistry::DB()->execute();
					array_push($groups, ipsRegistry::DB()->fetch($result));
				}
			}
			$this->classApiServer->apiSendReply($groups);
			
			exit();
		}
	}
	
	
	public function addGroup( $api_key, $api_module, $group)
	{
		//-----------------------------------------
		// INIT
		//-----------------------------------------

		$api_key	= IPSText::md5Clean( $api_key );
		$api_module	= IPSText::parseCleanValue( $api_module );
		
		//-----------------------------------------
		// Authenticate
		//-----------------------------------------
		
		if ( $this->__authenticate( $api_key, $api_module, 'addGroup' ) !== FALSE )
		{
			
			//-----------------------------------------
			// Add log
			//-----------------------------------------
			$this->addLogging( $api_key );

			$result = ipsRegistry::DB()->insert("groups", array('g_title'=>$group));
			ipsRegistry::DB()->fetch($result);
			
			// Rebuild the group cache
			ipsRegistry::cache()->rebuildCache( 'group_cache', 'global' );
			
			// Regardless if it passes or fails it will only fail if it exist
			$this->classApiServer->apiSendReply(array('result'=>'success'));
			
			exit();
		}
	}
	
	public function addUserToGroup( $api_key, $api_module, $username, $group)
	{
		//-----------------------------------------
		// INIT
		//-----------------------------------------

		$api_key	= IPSText::md5Clean( $api_key );
		$api_module	= IPSText::parseCleanValue( $api_module );
		
		//-----------------------------------------
		// Authenticate
		//-----------------------------------------
		
		if ( $this->__authenticate( $api_key, $api_module, 'addUserToGroup' ) !== FALSE )
		{
			
			//-----------------------------------------
			// Add log
			//-----------------------------------------
			$this->addLogging( $api_key );

			$member = IPSMember::load($username,'all','username');
			$groups = explode(",", $member['mgroup_others']);
			
			// Group group id
			ipsRegistry::DB()->build(array('select' => 'g_id', 'from' => 'groups', 'where'=>"g_title='{$group}'"));
			$result = ipsRegistry::DB()->execute();
			array_push($groups, ipsRegistry::DB()->fetch($result)['g_id']);
			
			$groupstoadd = implode(",", $groups);
			IPSMember::save( array( 'core' => array( 'field' => 'member_id', 'value' => $member['member_id'])),array('core' => array('mgroup_others'=>$groupstoadd)));
			
			// Rebuild the group cache
			ipsRegistry::cache()->rebuildCache( 'group_cache', 'global' );
			
			$this->classApiServer->apiSendReply($groups);
			
			exit();
		}
	}
	
	public function removeUserFromGroup( $api_key, $api_module, $username, $group)
	{
		//-----------------------------------------
		// INIT
		//-----------------------------------------

		$api_key	= IPSText::md5Clean( $api_key );
		$api_module	= IPSText::parseCleanValue( $api_module );
		
		//-----------------------------------------
		// Authenticate
		//-----------------------------------------
		
		if ( $this->__authenticate( $api_key, $api_module, 'removeUserFromGroup' ) !== FALSE )
		{
			
			//-----------------------------------------
			// Add log
			//-----------------------------------------
			$this->addLogging( $api_key );

			$member = IPSMember::load($username,'all','username');
			$groups = explode(",", $member['mgroup_others']);
			
			// Group group id
			ipsRegistry::DB()->build(array('select' => 'g_id', 'from' => 'groups', 'where'=>"g_title='{$group}'"));
			$result = ipsRegistry::DB()->execute();
			$diffGroup = array_diff($groups, array(ipsRegistry::DB()->fetch($result)['g_id']));
			
			$groupstoadd = implode(",", $diffGroup);
			IPSMember::save( array( 'core' => array( 'field' => 'member_id', 'value' => $member['member_id'])),array('core' => array('mgroup_others'=>$groupstoadd)));
			
			// Rebuild the group cache
			ipsRegistry::cache()->rebuildCache( 'group_cache', 'global' );
			
			$this->classApiServer->apiSendReply($diffGroup);
			
			exit();
		}
	}
	
	public function helpMe( $api_key, $api_module)
	{
		//-----------------------------------------
		// INIT
		//-----------------------------------------

		$api_key	= IPSText::md5Clean( $api_key );
		$api_module	= IPSText::parseCleanValue( $api_module );
		
		//-----------------------------------------
		// Authenticate
		//-----------------------------------------
		
		if ( $this->__authenticate( $api_key, $api_module, 'helpMe' ) !== FALSE )
		{
			
			//-----------------------------------------
			// Add log
			//-----------------------------------------
			$this->addLogging( $api_key );

			
			$this->classApiServer->apiSendReply($groups);
			
			exit();
		}
	}
	
	/**
	 * Adds logging obviously :)
	 *
	 * @param	string  $api_key		Authentication Key
	 */
	public function addLogging( $api_key )
	{
		if ( ipsRegistry::$settings['xmlrpc_log_type'] != 'failed' )
		{
			$this->registry->DB()->insert( 'api_log', array(   'api_log_key'     => $api_key,
					'api_log_ip'      => $_SERVER['REMOTE_ADDR'],
					'api_log_date'    => time(),
					'api_log_query'   => $this->classApiServer->raw_request,
					'api_log_allowed' => 1 ) );
		}
	}	
	
	/**
	 * Checks to see if the request is allowed
	 * 
	 * @param	string	$api_key		Authenticate Key
	 * @param	string	$api_module		Module
	 * @param	string	$api_function	Function 
	 * @return	string	Error message, if any
	 */
	protected function __authenticate( $api_key, $api_module, $api_function )
	{
		//-----------------------------------------
		// Check
		//-----------------------------------------
		
		if ( $this->api_user['api_user_id'] )
		{
			$this->api_user['_permissions'] = unserialize( stripslashes( $this->api_user['api_user_perms'] ) );
			
			if ( $this->api_user['_permissions'][ $api_module ][ $api_function ] == 1 )
			{
				return TRUE;
			}
			else
			{
				$this->registry->DB()->insert( 'api_log', array(   'api_log_key'     => $api_key,
																	'api_log_ip'      => $_SERVER['REMOTE_ADDR'],
																	'api_log_date'    => time(),
																	'api_log_query'   => $this->classApiServer->raw_request,
																	'api_log_allowed' => 0 ) );
				
				$this->classApiServer->apiSendError( '200', "API Key {$api_key} does not have permission for {$api_module}/{$api_function}" );

				return FALSE;
			}
		}
		else
		{
			$this->registry->DB()->insert( 'api_log', array(   'api_log_key'     => $api_key,
																'api_log_ip'      => $_SERVER['REMOTE_ADDR'],
																'api_log_date'    => time(),
																'api_log_query'   => $this->classApiServer->raw_request,
																'api_log_allowed' => 0 ) );
			
			$this->classApiServer->apiSendError( '100', "API Key {$api_key} does not have permission for {$api_module}/{$api_function}" );
																																						
			return FALSE;
		}
	}

}