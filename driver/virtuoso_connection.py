#!/usr/bin/env python
#-*- coding:utf-8 -*-
import pycurl
import urllib
import time
import StringIO
import traceback
import simplejson

from django.conf import settings

class VirtuosoConnection(object):
    """
    VirtuosoConnection class provide a simple http driver to run virtuoso
    queries
    """
    semantic_logger = settings.log_semantica

    def __init__(self):
        """
        Init connection getting url to request queries
        """
        self.url = settings.SEMANTICA_ENDPOINT

    def query(self, query):
        """
        Run a query in virtuoso

        @query: String of query that be runned

        Returns: A dictionary with the data getted by Virtuoso
        """
        curl = pycurl.Curl()

        body = {"query": query, "format": "application/sparql-results+json"}
        body_encoded = urllib.urlencode(body)
        url = "http://%s/sparql?%s" % (self.url, body_encoded.encode("utf-8"))

        try:
            start_time = time.time()
            response = self._virtuoso(url, curl)
            end_time = time.time()
            difference = end_time - start_time

            self.semantic_logger.info(
                "[TIME: %f] - QUERY - %s" % (
                    difference,
                    query
                )
            )

            if (difference >= 1.0):
                self.semantic_logger.warn(
                    "WARNING: Slow query! The next query is runned in %f: \n \
                    %s" % (difference, query)
                )
        except Exception, e:
            self.semantic_logger.error(
                "[VIRTUOSO CONNECTION ERROR] Virtuoso connection error - QUERY \
                - %s" % query)
            raise e

        return response

    def _virtuoso(self, url, curl):
        """
        Query a Virtuoso connection and call the url of query

        @url: String of url query (as a get url)
        @curl: The curl object

        Returns: A dictionary with the data getted by Virtuoso
        """
        reader = StringIO.StringIO()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.TIMEOUT, 30)
        curl.setopt(pycurl.CONNECTTIMEOUT, 5)
        curl.setopt(pycurl.NOSIGNAL, 1)
        curl.setopt(pycurl.WRITEFUNCTION, reader.write)
        try:
            curl.perform()
            status = curl.getinfo(pycurl.HTTP_CODE)
            curl.close()
        except:
            self.semantic_logger.error(
                "[VIRTUOSO CONNECTION ERROR] PyCurl connection error. %s" % \
                str(traceback.format_exc())
            )
            raise RuntimeError(
                "PyCurl connection error. Message: %s" % \
                 str(traceback.format_exc())
            )

        if (status == 200):
            content = reader.getvalue()
            reader.close()
            return simplejson.loads(content)
        elif (status == 400):
            self.semantic_logger.error(
                "[VIRTUOSO CONNECTION - BAD QUERY]: Can not run the query. \
                Probably is a bad query" % status)
            raise RuntimeError("[VIRTUOSO CONNECTION - BAD QUERY]: Can not run \
                the query. Probably is a bad query")
        else:
            self.semantic_logger.error("[VIRTUOSO CONNECTION ERROR] Virtuoso \
                connection error. %s" % str(traceback.format_exc()))
            self.semantic_logger.error("[VIRTUOSO CONNECTION ERROR] Status: \
                %s"  % status)
            raise RuntimeError("Virtuoso Connection errror. Status: %s" % status)
