"""
    Svix API

    Welcome to the Svix API documentation!  Useful links: [Homepage](https://www.svix.com) | [Support email](mailto:support+docs@svix.com) | [Blog](https://www.svix.com/blog/) | [Slack Community](https://www.svix.com/slack/)  # Introduction  This is the reference documentation and schemas for the [Svix webhook service](https://www.svix.com) API. For tutorials and other documentation please refer to [the documentation](https://docs.svix.com).  ## Main concepts  In Svix you have four important entities you will be interacting with:  - `messages`: these are the webhooks being sent. They can have contents and a few other properties. - `application`: this is where `messages` are sent to. Usually you want to create one application for each user on your platform. - `endpoint`: endpoints are the URLs messages will be sent to. Each application can have multiple `endpoints` and each message sent to that application will be sent to all of them (unless they are not subscribed to the sent event type). - `event-type`: event types are identifiers denoting the type of the message being sent. Event types are primarily used to decide which events are sent to which endpoint.   ## Authentication  Get your authentication token (`AUTH_TOKEN`) from the [Svix dashboard](https://dashboard.svix.com) and use it as part of the `Authorization` header as such: `Authorization: Bearer ${AUTH_TOKEN}`.  <SecurityDefinitions />   ## Code samples  The code samples assume you already have the respective libraries installed and you know how to use them. For the latest information on how to do that, please refer to [the documentation](https://docs.svix.com/).   ## Idempotency  Svix supports [idempotency](https://en.wikipedia.org/wiki/Idempotence) for safely retrying requests without accidentally performing the same operation twice. This is useful when an API call is disrupted in transit and you do not receive a response.  To perform an idempotent request, pass the idempotency key in the `Idempotency-Key` header to the request. The idempotency key should be a unique value generated by the client. You can create the key in however way you like, though we suggest using UUID v4, or any other string with enough entropy to avoid collisions.  Svix's idempotency works by saving the resulting status code and body of the first request made for any given idempotency key for any successful request. Subsequent requests with the same key return the same result.  Please note that idempotency is only supported for `POST` requests.   ## Cross-Origin Resource Sharing  This API features Cross-Origin Resource Sharing (CORS) implemented in compliance with [W3C spec](https://www.w3.org/TR/cors/). And that allows cross-domain communication from the browser. All responses have a wildcard same-origin which makes them completely public and accessible to everyone, including any code on any site.   # noqa: E501

    The version of the OpenAPI document: 1.4
    Generated by: https://openapi-generator.tech
"""


import re  # noqa: F401
import sys  # noqa: F401

from svix.openapi_client.api_client import ApiClient, Endpoint as _Endpoint
from svix.openapi_client.model_utils import (  # noqa: F401
    check_allowed_values,
    check_validations,
    date,
    datetime,
    file_type,
    none_type,
    validate_and_convert_types
)
from svix.openapi_client.model.application_in import ApplicationIn
from svix.openapi_client.model.application_out import ApplicationOut
from svix.openapi_client.model.http_validation_error import HTTPValidationError
from svix.openapi_client.model.http_error_out import HttpErrorOut
from svix.openapi_client.model.list_response_application_out import ListResponseApplicationOut


class ApplicationApi(object):
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client

        def __create_application_api_v1_app_post(
            self,
            application_in,
            **kwargs
        ):
            """Create Application  # noqa: E501

            Create a new application.  # noqa: E501
            This method makes a synchronous HTTP request by default. To make an
            asynchronous HTTP request, please pass async_req=True

            >>> thread = api.create_application_api_v1_app_post(application_in, async_req=True)
            >>> result = thread.get()

            Args:
                application_in (ApplicationIn):

            Keyword Args:
                _return_http_data_only (bool): response data without head status
                    code and headers. Default is True.
                _preload_content (bool): if False, the urllib3.HTTPResponse object
                    will be returned without reading/decoding response data.
                    Default is True.
                _request_timeout (int/float/tuple): timeout setting for this request. If
                    one number provided, it will be total request timeout. It can also
                    be a pair (tuple) of (connection, read) timeouts.
                    Default is None.
                _check_input_type (bool): specifies if type checking
                    should be done one the data sent to the server.
                    Default is True.
                _check_return_type (bool): specifies if type checking
                    should be done one the data received from the server.
                    Default is True.
                _host_index (int/None): specifies the index of the server
                    that we want to use.
                    Default is read from the configuration.
                async_req (bool): execute request asynchronously

            Returns:
                ApplicationOut
                    If the method is called asynchronously, returns the request
                    thread.
            """
            kwargs['async_req'] = kwargs.get(
                'async_req', False
            )
            kwargs['_return_http_data_only'] = kwargs.get(
                '_return_http_data_only', True
            )
            kwargs['_preload_content'] = kwargs.get(
                '_preload_content', True
            )
            kwargs['_request_timeout'] = kwargs.get(
                '_request_timeout', None
            )
            kwargs['_check_input_type'] = kwargs.get(
                '_check_input_type', True
            )
            kwargs['_check_return_type'] = kwargs.get(
                '_check_return_type', True
            )
            kwargs['_host_index'] = kwargs.get('_host_index')
            kwargs['application_in'] = \
                application_in
            return self.call_with_http_info(**kwargs)

        self.create_application_api_v1_app_post = _Endpoint(
            settings={
                'response_type': (ApplicationOut,),
                'auth': [
                    'HTTPBearer'
                ],
                'endpoint_path': '/api/v1/app/',
                'operation_id': 'create_application_api_v1_app_post',
                'http_method': 'POST',
                'servers': None,
            },
            params_map={
                'all': [
                    'application_in',
                ],
                'required': [
                    'application_in',
                ],
                'nullable': [
                ],
                'enum': [
                ],
                'validation': [
                ]
            },
            root_map={
                'validations': {
                },
                'allowed_values': {
                },
                'openapi_types': {
                    'application_in':
                        (ApplicationIn,),
                },
                'attribute_map': {
                },
                'location_map': {
                    'application_in': 'body',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'accept': [
                    'application/json'
                ],
                'content_type': [
                    'application/json'
                ]
            },
            api_client=api_client,
            callable=__create_application_api_v1_app_post
        )

        def __delete_application_api_v1_app_app_id_delete(
            self,
            app_id,
            **kwargs
        ):
            """Delete Application  # noqa: E501

            Delete an application.  # noqa: E501
            This method makes a synchronous HTTP request by default. To make an
            asynchronous HTTP request, please pass async_req=True

            >>> thread = api.delete_application_api_v1_app_app_id_delete(app_id, async_req=True)
            >>> result = thread.get()

            Args:
                app_id (str):

            Keyword Args:
                _return_http_data_only (bool): response data without head status
                    code and headers. Default is True.
                _preload_content (bool): if False, the urllib3.HTTPResponse object
                    will be returned without reading/decoding response data.
                    Default is True.
                _request_timeout (int/float/tuple): timeout setting for this request. If
                    one number provided, it will be total request timeout. It can also
                    be a pair (tuple) of (connection, read) timeouts.
                    Default is None.
                _check_input_type (bool): specifies if type checking
                    should be done one the data sent to the server.
                    Default is True.
                _check_return_type (bool): specifies if type checking
                    should be done one the data received from the server.
                    Default is True.
                _host_index (int/None): specifies the index of the server
                    that we want to use.
                    Default is read from the configuration.
                async_req (bool): execute request asynchronously

            Returns:
                None
                    If the method is called asynchronously, returns the request
                    thread.
            """
            kwargs['async_req'] = kwargs.get(
                'async_req', False
            )
            kwargs['_return_http_data_only'] = kwargs.get(
                '_return_http_data_only', True
            )
            kwargs['_preload_content'] = kwargs.get(
                '_preload_content', True
            )
            kwargs['_request_timeout'] = kwargs.get(
                '_request_timeout', None
            )
            kwargs['_check_input_type'] = kwargs.get(
                '_check_input_type', True
            )
            kwargs['_check_return_type'] = kwargs.get(
                '_check_return_type', True
            )
            kwargs['_host_index'] = kwargs.get('_host_index')
            kwargs['app_id'] = \
                app_id
            return self.call_with_http_info(**kwargs)

        self.delete_application_api_v1_app_app_id_delete = _Endpoint(
            settings={
                'response_type': None,
                'auth': [
                    'HTTPBearer'
                ],
                'endpoint_path': '/api/v1/app/{app_id}/',
                'operation_id': 'delete_application_api_v1_app_app_id_delete',
                'http_method': 'DELETE',
                'servers': None,
            },
            params_map={
                'all': [
                    'app_id',
                ],
                'required': [
                    'app_id',
                ],
                'nullable': [
                ],
                'enum': [
                ],
                'validation': [
                    'app_id',
                ]
            },
            root_map={
                'validations': {
                    ('app_id',): {
                        'max_length': 256,
                        'min_length': 1,
                        'regex': {
                            'pattern': r'^[a-zA-Z0-9\-_.]+$',  # noqa: E501
                        },
                    },
                },
                'allowed_values': {
                },
                'openapi_types': {
                    'app_id':
                        (str,),
                },
                'attribute_map': {
                    'app_id': 'app_id',
                },
                'location_map': {
                    'app_id': 'path',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'accept': [
                    'application/json'
                ],
                'content_type': [],
            },
            api_client=api_client,
            callable=__delete_application_api_v1_app_app_id_delete
        )

        def __get_application_api_v1_app_app_id_get(
            self,
            app_id,
            **kwargs
        ):
            """Get Application  # noqa: E501

            Get an application.  # noqa: E501
            This method makes a synchronous HTTP request by default. To make an
            asynchronous HTTP request, please pass async_req=True

            >>> thread = api.get_application_api_v1_app_app_id_get(app_id, async_req=True)
            >>> result = thread.get()

            Args:
                app_id (str):

            Keyword Args:
                _return_http_data_only (bool): response data without head status
                    code and headers. Default is True.
                _preload_content (bool): if False, the urllib3.HTTPResponse object
                    will be returned without reading/decoding response data.
                    Default is True.
                _request_timeout (int/float/tuple): timeout setting for this request. If
                    one number provided, it will be total request timeout. It can also
                    be a pair (tuple) of (connection, read) timeouts.
                    Default is None.
                _check_input_type (bool): specifies if type checking
                    should be done one the data sent to the server.
                    Default is True.
                _check_return_type (bool): specifies if type checking
                    should be done one the data received from the server.
                    Default is True.
                _host_index (int/None): specifies the index of the server
                    that we want to use.
                    Default is read from the configuration.
                async_req (bool): execute request asynchronously

            Returns:
                ApplicationOut
                    If the method is called asynchronously, returns the request
                    thread.
            """
            kwargs['async_req'] = kwargs.get(
                'async_req', False
            )
            kwargs['_return_http_data_only'] = kwargs.get(
                '_return_http_data_only', True
            )
            kwargs['_preload_content'] = kwargs.get(
                '_preload_content', True
            )
            kwargs['_request_timeout'] = kwargs.get(
                '_request_timeout', None
            )
            kwargs['_check_input_type'] = kwargs.get(
                '_check_input_type', True
            )
            kwargs['_check_return_type'] = kwargs.get(
                '_check_return_type', True
            )
            kwargs['_host_index'] = kwargs.get('_host_index')
            kwargs['app_id'] = \
                app_id
            return self.call_with_http_info(**kwargs)

        self.get_application_api_v1_app_app_id_get = _Endpoint(
            settings={
                'response_type': (ApplicationOut,),
                'auth': [
                    'HTTPBearer'
                ],
                'endpoint_path': '/api/v1/app/{app_id}/',
                'operation_id': 'get_application_api_v1_app_app_id_get',
                'http_method': 'GET',
                'servers': None,
            },
            params_map={
                'all': [
                    'app_id',
                ],
                'required': [
                    'app_id',
                ],
                'nullable': [
                ],
                'enum': [
                ],
                'validation': [
                    'app_id',
                ]
            },
            root_map={
                'validations': {
                    ('app_id',): {
                        'max_length': 256,
                        'min_length': 1,
                        'regex': {
                            'pattern': r'^[a-zA-Z0-9\-_.]+$',  # noqa: E501
                        },
                    },
                },
                'allowed_values': {
                },
                'openapi_types': {
                    'app_id':
                        (str,),
                },
                'attribute_map': {
                    'app_id': 'app_id',
                },
                'location_map': {
                    'app_id': 'path',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'accept': [
                    'application/json'
                ],
                'content_type': [],
            },
            api_client=api_client,
            callable=__get_application_api_v1_app_app_id_get
        )

        def __list_applications_api_v1_app_get(
            self,
            **kwargs
        ):
            """List Applications  # noqa: E501

            List of all the organization's applications.  # noqa: E501
            This method makes a synchronous HTTP request by default. To make an
            asynchronous HTTP request, please pass async_req=True

            >>> thread = api.list_applications_api_v1_app_get(async_req=True)
            >>> result = thread.get()


            Keyword Args:
                iterator (str): [optional]
                limit (int): [optional] if omitted the server will use the default value of 50
                _return_http_data_only (bool): response data without head status
                    code and headers. Default is True.
                _preload_content (bool): if False, the urllib3.HTTPResponse object
                    will be returned without reading/decoding response data.
                    Default is True.
                _request_timeout (int/float/tuple): timeout setting for this request. If
                    one number provided, it will be total request timeout. It can also
                    be a pair (tuple) of (connection, read) timeouts.
                    Default is None.
                _check_input_type (bool): specifies if type checking
                    should be done one the data sent to the server.
                    Default is True.
                _check_return_type (bool): specifies if type checking
                    should be done one the data received from the server.
                    Default is True.
                _host_index (int/None): specifies the index of the server
                    that we want to use.
                    Default is read from the configuration.
                async_req (bool): execute request asynchronously

            Returns:
                ListResponseApplicationOut
                    If the method is called asynchronously, returns the request
                    thread.
            """
            kwargs['async_req'] = kwargs.get(
                'async_req', False
            )
            kwargs['_return_http_data_only'] = kwargs.get(
                '_return_http_data_only', True
            )
            kwargs['_preload_content'] = kwargs.get(
                '_preload_content', True
            )
            kwargs['_request_timeout'] = kwargs.get(
                '_request_timeout', None
            )
            kwargs['_check_input_type'] = kwargs.get(
                '_check_input_type', True
            )
            kwargs['_check_return_type'] = kwargs.get(
                '_check_return_type', True
            )
            kwargs['_host_index'] = kwargs.get('_host_index')
            return self.call_with_http_info(**kwargs)

        self.list_applications_api_v1_app_get = _Endpoint(
            settings={
                'response_type': (ListResponseApplicationOut,),
                'auth': [
                    'HTTPBearer'
                ],
                'endpoint_path': '/api/v1/app/',
                'operation_id': 'list_applications_api_v1_app_get',
                'http_method': 'GET',
                'servers': None,
            },
            params_map={
                'all': [
                    'iterator',
                    'limit',
                ],
                'required': [],
                'nullable': [
                ],
                'enum': [
                ],
                'validation': [
                    'limit',
                ]
            },
            root_map={
                'validations': {
                    ('limit',): {

                        'inclusive_maximum': 250,
                    },
                },
                'allowed_values': {
                },
                'openapi_types': {
                    'iterator':
                        (str,),
                    'limit':
                        (int,),
                },
                'attribute_map': {
                    'iterator': 'iterator',
                    'limit': 'limit',
                },
                'location_map': {
                    'iterator': 'query',
                    'limit': 'query',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'accept': [
                    'application/json'
                ],
                'content_type': [],
            },
            api_client=api_client,
            callable=__list_applications_api_v1_app_get
        )

        def __update_application_api_v1_app_app_id_put(
            self,
            app_id,
            application_in,
            **kwargs
        ):
            """Update Application  # noqa: E501

            Update an application.  # noqa: E501
            This method makes a synchronous HTTP request by default. To make an
            asynchronous HTTP request, please pass async_req=True

            >>> thread = api.update_application_api_v1_app_app_id_put(app_id, application_in, async_req=True)
            >>> result = thread.get()

            Args:
                app_id (str):
                application_in (ApplicationIn):

            Keyword Args:
                _return_http_data_only (bool): response data without head status
                    code and headers. Default is True.
                _preload_content (bool): if False, the urllib3.HTTPResponse object
                    will be returned without reading/decoding response data.
                    Default is True.
                _request_timeout (int/float/tuple): timeout setting for this request. If
                    one number provided, it will be total request timeout. It can also
                    be a pair (tuple) of (connection, read) timeouts.
                    Default is None.
                _check_input_type (bool): specifies if type checking
                    should be done one the data sent to the server.
                    Default is True.
                _check_return_type (bool): specifies if type checking
                    should be done one the data received from the server.
                    Default is True.
                _host_index (int/None): specifies the index of the server
                    that we want to use.
                    Default is read from the configuration.
                async_req (bool): execute request asynchronously

            Returns:
                ApplicationOut
                    If the method is called asynchronously, returns the request
                    thread.
            """
            kwargs['async_req'] = kwargs.get(
                'async_req', False
            )
            kwargs['_return_http_data_only'] = kwargs.get(
                '_return_http_data_only', True
            )
            kwargs['_preload_content'] = kwargs.get(
                '_preload_content', True
            )
            kwargs['_request_timeout'] = kwargs.get(
                '_request_timeout', None
            )
            kwargs['_check_input_type'] = kwargs.get(
                '_check_input_type', True
            )
            kwargs['_check_return_type'] = kwargs.get(
                '_check_return_type', True
            )
            kwargs['_host_index'] = kwargs.get('_host_index')
            kwargs['app_id'] = \
                app_id
            kwargs['application_in'] = \
                application_in
            return self.call_with_http_info(**kwargs)

        self.update_application_api_v1_app_app_id_put = _Endpoint(
            settings={
                'response_type': (ApplicationOut,),
                'auth': [
                    'HTTPBearer'
                ],
                'endpoint_path': '/api/v1/app/{app_id}/',
                'operation_id': 'update_application_api_v1_app_app_id_put',
                'http_method': 'PUT',
                'servers': None,
            },
            params_map={
                'all': [
                    'app_id',
                    'application_in',
                ],
                'required': [
                    'app_id',
                    'application_in',
                ],
                'nullable': [
                ],
                'enum': [
                ],
                'validation': [
                    'app_id',
                ]
            },
            root_map={
                'validations': {
                    ('app_id',): {
                        'max_length': 256,
                        'min_length': 1,
                        'regex': {
                            'pattern': r'^[a-zA-Z0-9\-_.]+$',  # noqa: E501
                        },
                    },
                },
                'allowed_values': {
                },
                'openapi_types': {
                    'app_id':
                        (str,),
                    'application_in':
                        (ApplicationIn,),
                },
                'attribute_map': {
                    'app_id': 'app_id',
                },
                'location_map': {
                    'app_id': 'path',
                    'application_in': 'body',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'accept': [
                    'application/json'
                ],
                'content_type': [
                    'application/json'
                ]
            },
            api_client=api_client,
            callable=__update_application_api_v1_app_app_id_put
        )
