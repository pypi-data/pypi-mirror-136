"""
    NCBI Datasets API

    ### NCBI Datasets is a resource that lets you easily gather data from NCBI. The Datasets API is still in alpha, and we're updating it often to add new functionality, iron out bugs and enhance usability. For some larger downloads, you may want to download a [dehydrated bag](https://www.ncbi.nlm.nih.gov/datasets/docs/rehydrate/), and retrieve the individual data files at a later time.   # noqa: E501

    The version of the OpenAPI document: v1
    Generated by: https://openapi-generator.tech
"""


import re  # noqa: F401
import sys  # noqa: F401

from ncbi.datasets.openapi.api_client import ApiClient, Endpoint as _Endpoint
from ncbi.datasets.openapi.model_utils import (  # noqa: F401
    check_allowed_values,
    check_validations,
    date,
    datetime,
    file_type,
    none_type,
    validate_and_convert_types
)
from ncbi.datasets.openapi.model.rpc_status import RpcStatus
from ncbi.datasets.openapi.model.v1_fasta import V1Fasta
from ncbi.datasets.openapi.model.v1_prokaryote_gene_request import V1ProkaryoteGeneRequest


class ProkaryoteApi(object):
    """NOTE: This class is auto generated by OpenAPI Generator
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    def __init__(self, api_client=None):
        if api_client is None:
            api_client = ApiClient()
        self.api_client = api_client
        self.download_prokaryote_gene_package_endpoint = _Endpoint(
            settings={
                'response_type': (file_type,),
                'auth': [
                    'ApiKeyAuthHeader'
                ],
                'endpoint_path': '/protein/accession/{accessions}/download',
                'operation_id': 'download_prokaryote_gene_package',
                'http_method': 'GET',
                'servers': None,
            },
            params_map={
                'all': [
                    'accessions',
                    'include_annotation_type',
                    'gene_flank_config_length',
                    'taxon',
                    'filename',
                ],
                'required': [
                    'accessions',
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
                    'accessions':
                        ([str],),
                    'include_annotation_type':
                        ([V1Fasta],),
                    'gene_flank_config_length':
                        (int,),
                    'taxon':
                        (str,),
                    'filename':
                        (str,),
                },
                'attribute_map': {
                    'accessions': 'accessions',
                    'include_annotation_type': 'include_annotation_type',
                    'gene_flank_config_length': 'gene_flank_config.length',
                    'taxon': 'taxon',
                    'filename': 'filename',
                },
                'location_map': {
                    'accessions': 'path',
                    'include_annotation_type': 'query',
                    'gene_flank_config_length': 'query',
                    'taxon': 'query',
                    'filename': 'query',
                },
                'collection_format_map': {
                    'accessions': 'csv',
                    'include_annotation_type': 'multi',
                }
            },
            headers_map={
                'accept': [
                    'application/zip',
                    'application/json'
                ],
                'content_type': [],
            },
            api_client=api_client
        )
        self.download_prokaryote_gene_package_post_endpoint = _Endpoint(
            settings={
                'response_type': (file_type,),
                'auth': [
                    'ApiKeyAuthHeader'
                ],
                'endpoint_path': '/protein/accession/download',
                'operation_id': 'download_prokaryote_gene_package_post',
                'http_method': 'POST',
                'servers': None,
            },
            params_map={
                'all': [
                    'v1_prokaryote_gene_request',
                    'filename',
                ],
                'required': [
                    'v1_prokaryote_gene_request',
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
                    'v1_prokaryote_gene_request':
                        (V1ProkaryoteGeneRequest,),
                    'filename':
                        (str,),
                },
                'attribute_map': {
                    'filename': 'filename',
                },
                'location_map': {
                    'v1_prokaryote_gene_request': 'body',
                    'filename': 'query',
                },
                'collection_format_map': {
                }
            },
            headers_map={
                'accept': [
                    'application/zip',
                    'application/json'
                ],
                'content_type': [
                    'application/json'
                ]
            },
            api_client=api_client
        )

    def download_prokaryote_gene_package(
        self,
        accessions,
        **kwargs
    ):
        """Get a prokaryote gene dataset by RefSeq protein accession  # noqa: E501

        Get a prokaryote gene dataset including gene and protein fasta sequence, annotation and metadata by prokaryote protein accession.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.download_prokaryote_gene_package(accessions, async_req=True)
        >>> result = thread.get()

        Args:
            accessions ([str]): WP prokaryote protein accession

        Keyword Args:
            include_annotation_type ([V1Fasta]): Select additional types of annotation to include in the data package.  If unset, no annotation is provided.. [optional]
            gene_flank_config_length (int): [optional]
            taxon (str): NCBI Taxonomy ID or name (common or scientific) at any taxonomic rank When specified, return data from this taxon and its subtree. [optional]
            filename (str): Output file name.. [optional] if omitted the server will use the default value of "ncbi_dataset.zip"
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
            file_type
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
        kwargs['accessions'] = \
            accessions
        headers = kwargs.get('headers', {})
        if headers:
            accept = headers.get('accept') or headers.get('Accept')
            if accept and accept in self.gene_download_summary_by_accession_endpoint.headers_map:
                self.gene_download_summary_by_accession_endpoint.headers_map['accept'] = accept

            for key in headers.keys():
                self.gene_download_summary_by_accession_endpoint.headers_map[key] = headers[key]

        return self.download_prokaryote_gene_package_endpoint.call_with_http_info(**kwargs)

    def download_prokaryote_gene_package_post(
        self,
        v1_prokaryote_gene_request,
        **kwargs
    ):
        """Get a prokaryote gene dataset by RefSeq protein accession by POST  # noqa: E501

        Get a prokaryote gene dataset including gene and protein fasta sequence, annotation and metadata by prokaryote protein accession by POST.  # noqa: E501
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please pass async_req=True

        >>> thread = api.download_prokaryote_gene_package_post(v1_prokaryote_gene_request, async_req=True)
        >>> result = thread.get()

        Args:
            v1_prokaryote_gene_request (V1ProkaryoteGeneRequest):

        Keyword Args:
            filename (str): Output file name.. [optional] if omitted the server will use the default value of "ncbi_dataset.zip"
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
            file_type
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
        kwargs['v1_prokaryote_gene_request'] = \
            v1_prokaryote_gene_request
        headers = kwargs.get('headers', {})
        if headers:
            accept = headers.get('accept') or headers.get('Accept')
            if accept and accept in self.gene_download_summary_by_accession_endpoint.headers_map:
                self.gene_download_summary_by_accession_endpoint.headers_map['accept'] = accept

            for key in headers.keys():
                self.gene_download_summary_by_accession_endpoint.headers_map[key] = headers[key]

        return self.download_prokaryote_gene_package_post_endpoint.call_with_http_info(**kwargs)

