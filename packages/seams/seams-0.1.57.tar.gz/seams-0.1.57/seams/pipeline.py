#!/usr/bin/env python
from seams import Seams
from abc import ABC, abstractmethod
import os
import tempfile
import json
import calendar
import datetime
import traceback
import argparse
from seams.severity import Severity
class Pipeline(ABC):
    

    def __init__(self, EMAIL, PASSWORD, URL=None):
        '''
        Create an instance of the Pipeline interface
        '''
        self.result_files = []
        self.logs = []
        self.user_logs = []
        if URL:
            self.seams = Seams(URL)
        else:
            self.seams = Seams()
        self.seams.connect(EMAIL, PASSWORD)

    
    @abstractmethod
    def run(self, data):
        '''
        Abstract class that will be overwritten by the user
        '''
        print("ERROR: this method should be overridden")


    def start(self):
        '''
        starts a pipeline and does all the buildup and tear down for every pipeline

        :returns:
            JSON object representing the status of the completed pipeline
        '''
        try:
            #getting parameters and setting them to appropriate class variables
            parameters = self.__get_parameters()
            self.vertex_id = parameters['vertex_id']
            self.tenant_id = parameters['tenant_id']
            #setting pipeline status to IN PROGRESS
            self.update_pipeline_status_in_progress() 
            #getting the run parameters of pipeline
            data = json.loads(self.get_pipeline_run()['runParameters'])

            #downloading files
            self.log(Severity.INFO, "downloading files...")
            data['files'] = self.download_input_files()

            #running abstract run method
            self.run(data)
            #setting pipeline to DONE when finished
            return self.update_pipeline_status_done()
        except Exception as e:
            #if pipeline fails setting pipeline to ERROR and printing out the stack trace
            self.update_pipeline_status_error()
            self.log(Severity.ERROR, traceback.print_exc())


    def get_pipeline_run(self):
        '''
        get the pipeline vertex

        :returns:
            JSON object representing the pipeline vertex
        '''
        return self.seams.get_vertex_by_id(self.tenant_id, self.vertex_id)


    def update_pipeline_status_in_progress(self):
        '''
        sets the pipeline status to IN PROGRESS

        :returns:
            JSON object representing the status of the completed pipeline
        '''
        attributes = {
            "status": "IN PROGRESS"
        }
        return self.seams.update_vertex(self.tenant_id, self.vertex_id, "PipelineRun", attributes)
    

    def update_pipeline_status_done(self):
        '''
        sets the pipeline status to DONE

        :returns:
            JSON object representing the status of the completed pipeline
        '''
        attributes = {
            "status": "DONE",
            "runResults": self.result_files,
            "logs": self.logs,
            "userLogs": self.user_logs
        }
        return self.seams.update_vertex(self.tenant_id, self.vertex_id, "PipelineRun", attributes)


    def update_pipeline_status_error(self):
        '''
        sets the pipeline status to ERROR

        :returns:
            JSON object representing the status of the completed pipeline
        '''
        attributes = {
            "status": "ERROR",
            "runResults": self.result_files,
            "logs": self.logs,
            "userLogs": self.user_logs
        }
        return self.seams.update_vertex(self.tenant_id, self.vertex_id, "PipelineRun", attributes)


    def download_input_files(self):
        '''
        downloads any files needed by the pipeline

        :returns:
            list of file paths for files downloaded for the pipeline
        '''
        #gets the run parameters of the pipeline
        data = json.loads(self.seams.get_vertex_by_id(self.tenant_id, self.vertex_id)['runParameters'])
        files = []
        #downloads files in pipeline, adds them to a temp file, adds file path to a list
        for item in data['Files']:
            download = self.seams.download_files(self.tenant_id, item['vertexId'])
            for item in download:
                temp_file_full_path = os.path.join(tempfile.gettempdir(), item)
                files.append(temp_file_full_path)
                f = open(temp_file_full_path, 'w', encoding="utf-8")
                f.write(download[item])
                f.close()
        return files
    

    def upload_files(self, caption, files):
        '''
        uploads any files 

        :returns:
            JSON object representing the status of the upload
        '''
        return self.seams.upload_files(self.tenant_id, caption, files)


    def get_result_files(self):
        '''
        returns a list of all files created by the pipeline

        :returns:
            list of all files created by the pipelie
        '''
        return self.result_files


    def add_result_file(self, file_vertex_id, label, name):
        '''
        adds a new result file to the result files list

        '''
        new_file = {
            "id": file_vertex_id,
            "label": label, 
            "name": name
        }
        self.result_files.append(new_file)


    def log(self, log_severity, *args, for_user=False):
        '''
        logs any stdout or stderr and saves it to the pipeline run vertex
        '''
        #gets UTC time
        date = datetime.datetime.utcnow()
        utc_time = calendar.timegm(date.utctimetuple())
        result = ""
        #check if severity exists
        if isinstance(log_severity, Severity):
            for arg in args:
                if isinstance(arg, list):
                    result = result + " ".join(arg)
                elif isinstance(arg, dict):
                    result = result + json.dumps(arg)
                else:
                    result = result + str(arg)
            #creating log object
            log = {
                "severity": log_severity.name,
                "date": utc_time,
                "message": result
            }
            str_log = "{}   {}   {}".format(log['severity'], date, log['message'])
            print(str_log)
            self.logs.append(log)
            if for_user:
                self.user_logs.append(log)

    def __get_parameters(self):
        '''
        private method to get the parameters in a pipeline

        :returns:
            dict of all the command line arguments sent to the pipeline
        '''
        parser = argparse.ArgumentParser()
        parser.add_argument("tenant_id",
                            help="Vertex ID of the pipeline job")
        parser.add_argument("vertex_id",
                            help="Vertex ID of the pipeline job")

        args = parser.parse_args()
        if not (args.tenant_id and args.vertex_id):
            parser.error(
                "Tenant Id and Vertex Id required - do -h for help")

        parameters = {'tenant_id': args.tenant_id, 'vertex_id': args.vertex_id}
        return parameters
