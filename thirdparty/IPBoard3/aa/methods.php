<?php

/**
 * Remote API User Administration configuration
 * 
 * @author 		Author: Raynaldo Rivera 
 */
												
$ALLOWED_METHODS = array();

$ALLOWED_METHODS['createUser'] = array(
												   'in'  => array(
																	'api_key'           => 'string',
																	'api_module'        => 'string',
																	'username'     => 'string',
																	'email' => 'string',
																	'display_name'=> 'string',
																	'md5_passwordHash' => 'string'
															     ),
												   'out' => array(
																	'response' => 'xmlrpc'
																 )
												 );

$ALLOWED_METHODS['deleteUser'] = array(
												   'in'  => array(
																	'api_key'           => 'string',
																	'api_module'        => 'string',
																	'username'     => 'string'
															     ),
												   'out' => array(
																	'response' => 'xmlrpc'
																 )
												 );
												 
$ALLOWED_METHODS['disableUser'] = array(
												   'in'  => array(
																	'api_key'           => 'string',
																	'api_module'        => 'string',
																	'username'     => 'string'
															     ),
												   'out' => array(
																	'response' => 'xmlrpc'
																 )
												 );

$ALLOWED_METHODS['updateUser'] = array(
												   'in'  => array(
																	'api_key'           => 'string',
																	'api_module'        => 'string',
																	'username'     => 'string',
																	'email' => 'string',
																	'md5_passwordHash' => 'string'
															     ),
												   'out' => array(
																	'response' => 'xmlrpc'
																 )
												 );
												 
$ALLOWED_METHODS['getAllGroups'] = array(
												   'in'  => array(
																	'api_key'           => 'string',
																	'api_module'        => 'string',
															     ),
												   'out' => array(
																	'response' => 'xmlrpc'
																 )
												 );
												
$ALLOWED_METHODS['getUserGroups'] = array(
												   'in'  => array(
																	'api_key'           => 'string',
																	'api_module'        => 'string',
																	'username'          => 'string'
															     ),
												   'out' => array(
																	'response' => 'xmlrpc'
																 )
												 );
												 
$ALLOWED_METHODS['addGroup'] = array(
												   'in'  => array(
																	'api_key'           => 'string',
																	'api_module'        => 'string',
																	'group'          => 'string'
															     ),
												   'out' => array(
																	'response' => 'xmlrpc'
																 )
												 );
												 
$ALLOWED_METHODS['addUserToGroup'] = array(
												   'in'  => array(
																	'api_key'           => 'string',
																	'api_module'        => 'string',
																	'username'       => 'string',
																	'group'          => 'string'
															     ),
												   'out' => array(
																	'response' => 'xmlrpc'
																 )
												 );
												 
$ALLOWED_METHODS['removeUserFromGroup'] = array(
												   'in'  => array(
																	'api_key'           => 'string',
																	'api_module'        => 'string',
																	'username'       => 'string',
																	'group'          => 'string'
															     ),
												   'out' => array(
																	'response' => 'xmlrpc'
																 )
												 );
												 
$ALLOWED_METHODS['helpMe'] = array(
												   'in'  => array(
																	'api_key'           => 'string',
																	'api_module'        => 'string',

															     ),
												   'out' => array(
																	'response' => 'xmlrpc'
																 )
												 );