<?php


class MobileWorks {

	// user credentials
	protected $credentials = '';

	// the target domain
	public $domain = '';

	// the API version to be used
	protected $_version = 2;

	// username/password
	public $username = '', $password = '';

	protected $PROFILE_PATH = 'api/v1/userprofile/';

	public function __construct() {
		// This library depends on CURL for making HTTP requests
		if ( !extension_loaded( 'curl' ) ) {
			throw new Exception( 'CURL is not installed!' );
		}
		$this->sandbox();
	}

	public function production() {
		$this->domain = 'https://work.mobileworks.com/';
	}

	public function sandbox() {
		$this->domain = 'https://sandbox.mobileworks.com/';
	}

	public function version( $v = null ) {
		if ( is_null( $v ) ) {
			return $this->_version;
		}
		else {
			$this->_version = $v;
		}
	}

	function authenticate() {
		if ( empty( $this->username ) || empty( $this->password ) ) {
			throw new Exception( 'Please provide a username and password.' );
		}

		$new_credentials = $this->username . ':' . $this->password;
		if ( empty( $this->credentials ) || $this->credentials != $new_credentials ) {
			$this->credentials = $new_credentials;
			try {
				$this->make_request( $this->domain . $this->PROFILE_PATH );
			}
			catch ( Exception $e ) {
				$this->credentials = '';
				throw new Exception( "Authentication failed! To reset your password, please go to 'https://work.mobileworks.com/accounts/password_reset/'" );
			}
		}
		return $this->credentials;
	}

	/**
	 * Creates and sends a request to the specified $url using the specified $method.
	 * @param string $url The URL of the request.
	 * @param string $method The method of the request (GET/POST/DELETE).
	 * @param null|string|array $post_data  The data to be posted (optional).
	 * @return array The array representation of the returned JSON object.
	 * @throws Exception
	 */
	function make_request( $url, $method = 'GET', $post_data = null ) {
		$this->authenticate();

		$req = curl_init( $url );
		curl_setopt( $req, CURLOPT_CUSTOMREQUEST, $method );
		if ( $method == 'POST' && !is_null( $post_data ) ) {
			curl_setopt( $req, CURLOPT_POSTFIELDS, $post_data );
		}
		curl_setopt( $req, CURLOPT_HEADER, true );
		curl_setopt( $req, CURLOPT_RETURNTRANSFER, true );
		curl_setopt( $req, CURLOPT_HTTPAUTH, CURLAUTH_BASIC );
		curl_setopt( $req, CURLOPT_USERPWD, $this->credentials );

		$result = curl_exec( $req );
		if ( curl_errno( $req ) ) {
			$curl_error = curl_error( $req );
			curl_close( $req );
			throw new Exception( $curl_error );
		}

		$info = curl_getinfo( $req );

		$header = substr( $result, 0, $info['header_size'] );
		$content = substr( $result, $info['header_size'] );

		$http_code = curl_getinfo( $req, CURLINFO_HTTP_CODE );
		curl_close( $req );

		if ( $http_code >= 500 ) {
			throw new Exception( "HTTP $http_code: A server error occured!" );
		}
		if ( $http_code >= 300 ) {
			throw new Exception( "HTTP $http_code: $content" );
		}
		return array( 'headers' => $header, 'content' => $content );
	}

	public function Task( $params = null ) {
		$task = new Task( $this );
		if ( !is_null( $params ) ) {
			$task->set_params( $params );
		}
		return $task;
	}

	public function Project( $params = null ) {
		$project = new Project( $this );
		if ( !is_null( $params ) ) {
			$project->set_params( $params );
		}
		return $project;
	}

	public function retrieve( $location ) {
		if ( property_exists( $location, 'location' ) ) {
			$url = $location->location;
		}
		else {
			$url = $location;
		}

		$response = $this->make_request( $url );
		return json_decode( $response['content'], true );
	}

}

class Task {

	protected $mw = null;

	public $location = null;

	protected $params = array();

	protected $fields = null;

	function __construct( MobileWorks $mw ) {
		$this->mw = $mw;
	}

	protected function path() {
		$v = $this->mw->version();
		if ( $v == 1 ) {
			return 'api/v1/tasks/';
		}
		elseif ( $v == 2 ) {
			return 'api/v2/task/';
		}
		throw new Exception( "Sorry, version $v is not supported by the library yet!" );
	}

	function url() {
		return $this->mw->domain . $this->path();
	}

	function to_assoc() {
		$assoc = $this->params;
		if ( !is_null( $this->fields ) ) {
			$assoc['fields'] = $this->fields;
		}
		return $assoc;
	}

	function to_json() {
		return json_encode( $this->to_assoc() );
	}

	public function get_param( $name ) {
		return $this->params[$name];
	}

	public function set_param( $name, $value ) {
		$this->params[$name] = $value;
	}

	public function set_params( $params ) {
		foreach ( $params as $name => $value ) {
			$this->set_param( $name, $value );
		}
	}

	public function add_field( $name, $type, $extras = null ) {
		if ( $this->mw->version() < 2 ) {
			throw new Exception( "Fields only exist in version 2 of the API" );
		}

		if ( is_null( $this->fields ) ) {
			$this->fields = array();
		}

		$new_field = array( $name => $type );
		if ( !is_null( $extras ) ) {
			foreach ( $extras as $k => $v ) {
				$new_field[$k] = $v;
			}
		}
		$this->fields[] = $new_field;
	}

	public function post() {
		$response = $this->mw->make_request( $this->url(), 'POST', $this->to_json() );
		$v = $this->mw->version();
		if ( $v == 1 ) {
			var_dump( $response['headers'] );
			$this->location = '';
		}
		elseif( $v == 2 ) {
			$json = json_decode( $response['content'], true );
			$this->location = $json['Location'];
		}
		return $this->location;
	}

	public function delete() {
		if ( empty( $this->location ) ) {
			throw new Exception( "This object doesn't point to any resource on the server." );
		}
		$response = $this->mw->make_request( $this->location, 'DELETE' );
		$v = $this->mw->version();
		if ( $v == 1 ) {
			return true;
		}
		elseif ( $v ==2 ) {
			return json_decode( $response['content'], true );
		}
	}

}

class Project extends Task {

	protected $tasks = array();
	protected $test_tasks = null;

	protected function path() {
		$v = $this->mw->version();
		if ( $v == 1 ) {
			return 'api/v1/project/';
		}
		elseif ( $v == 2 ) {
			return 'api/v2/project/';
		}
		throw new Exception( "Sorry, version $v is not supported by the library yet!" );
	}

	public function add_task( $task ) {
		if ( method_exists( $task, 'to_assoc' ) ) {
			$this->tasks[] = $task;
		}
		else {
			throw new InvalidArgumentException( '`$task` must be a valid task object' );
		}
	}

	public function add_test_task( $test_task ) {
		if ( method_exists( $test_task, 'to_assoc' ) ) {
			if ( is_null( $this->test_tasks ) ) {
				$this->test_tasks = array();
			}
			$this->test_tasks[] = $test_task;
		}
		else {
			throw new InvalidArgumentException( '`$test_task` must be a valid task object' );
		}
	}

	function to_assoc() {
		$assoc = parent::to_assoc();
		if ( !is_null( $this->tasks ) ) {
			$assoc['tasks'] = array();
			foreach ( $this->tasks as $task ) {
				$assoc['tasks'][] = $task->to_assoc();
			}
		}
		if ( !is_null( $this->test_tasks ) ) {
			$assoc['tests'] = array();
			foreach ( $this->test_tasks as $task ) {
				$assoc['tests'][] = $task->to_assoc();
			}
		}
		return $assoc;
	}

}
