# SCAR - Serverless Container-aware ARchitectures
# Copyright (C) 2011 - GRyCAP - Universitat Politecnica de Valencia
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from src.providers.aws.clients.boto import BotoClient
import src.logger as logger
from botocore.exceptions import ClientError
import src.utils as utils

class CloudWatchLogsClient(BotoClient):
    '''A low-level client representing Amazon CloudWatch Logs.
    https://boto3.readthedocs.io/en/latest/reference/services/logs.html'''
    
    boto_client_name = 'logs'    
    
    @utils.exception(logger)    
    def get_log_events(self, log_group_name, log_stream_name=None):
        '''
        Lists log events from the specified log group.
        https://boto3.readthedocs.io/en/latest/reference/services/logs.html#CloudWatchLogs.Client.filter_log_events
        '''
        logs = []
        kwargs = {"logGroupName" : log_group_name}
        if log_stream_name:
            kwargs["logStreamNames"] = [log_stream_name]
        response = self.client.filter_log_events(**kwargs)
        logs.append(response)
        while ('nextToken' in response) and (response['nextToken']):
            kwargs['nextToken'] = response['nextToken']
            response = self.client.filter_log_events(**kwargs)
            logs.append(response)
        return logs
            
    @utils.exception(logger)            
    def create_log_group(self, log_group_name, tags):
        '''
        Creates a log group with the specified name.
        https://boto3.readthedocs.io/en/latest/reference/services/logs.html#CloudWatchLogs.Client.create_log_group
        '''         
        try:
            return self.client.create_log_group(logGroupName=log_group_name, tags=tags)
        except ClientError as ce:
            if ce.response['Error']['Code'] == 'ResourceAlreadyExistsException':
                logger.warning("Using existent log group '{0}'".format(log_group_name))
                pass
            else:
                raise
    
    @utils.exception(logger)
    def set_log_retention_policy(self, log_group_name, log_retention_policy_in_days):
        '''
        Sets the retention of the specified log group.
        https://boto3.readthedocs.io/en/latest/reference/services/logs.html#CloudWatchLogs.Client.put_retention_policy
        '''         
        return self.client.put_retention_policy(logGroupName=log_group_name, retentionInDays=log_retention_policy_in_days)
            
    @utils.exception(logger)
    def delete_log_group(self, log_group_name):
        '''
        Deletes the specified log group and permanently deletes all the archived log events associated with the log group.
        https://boto3.readthedocs.io/en/latest/reference/services/logs.html#CloudWatchLogs.Client.delete_log_group
        '''         
        try:
            return self.client.delete_log_group(logGroupName=log_group_name)
        except ClientError as ce:
            if ce.response['Error']['Code'] == 'ResourceNotFoundException':
                logger.warning("Cannot delete log group '%s'. Group not found." % log_group_name)
            else:
                raise
