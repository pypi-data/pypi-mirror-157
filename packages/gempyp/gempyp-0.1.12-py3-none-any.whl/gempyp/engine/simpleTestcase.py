from abc import ABC, abstractmethod
from typing import List, Union, Dict
from gempyp.config import DefaultSettings
from gempyp.engine.baseTemplate import testcaseReporter
from gempyp.libs.common import moduleImports
import sys,traceback
from gempyp.libs.enums.status import status
import logging


class AbstractSimpleTestcase(ABC):
    Status = status
    # get logger

    def gempypMethodExecutor(
        self, cls, testcaseSettings: Dict, **kwargs
    ) -> testcaseReporter:
        """
        extend the baseTemplate and implement this method.
        :param testcaseSettings: testcasesettings object created from the testcase config
        :return
        """
        logger = testcaseSettings.get("LOGGER")
        kwargs["TESTCASENAME"] = testcaseSettings["NAME"]
        file_name = testcaseSettings.get("PATH")
        try:
            testcase = moduleImports(file_name)
        except:
            logger.ERROR("Testcase not imported")
        try:
            methodName = testcaseSettings.get("METHOD", "main")
            logger.info(f"-------- method ---------{methodName}")
            reporter = testcaseReporter(kwargs["PROJECTNAME"], testcaseSettings["NAME"])
            # adding logger to the reporter
            reporter.logger = logger
            try:
                methodName = getattr(cls(), methodName)
                methodName(reporter)
            except Exception as err:
                logger.error(traceback.format_exc())
                etype, value, tb = sys.exc_info()
                info, error = traceback.format_exception(etype, value, tb)[-2:]
                #reports = testcaseReporter(kwargs["PROJECTNAME"], testcaseSettings["NAME"])
                reporter.addRow("Exception Occured", str(error) + 'at' + str(info), status.FAIL)
            finally:
                return reporter
                
        except Exception as e:
            if e:            
                logger.error(traceback.format_exc())
            
        

    def RUN(self, cls, testcaseSettings: Dict, **kwargs) -> List:
        """
        the main function which will be called by the executor
        """
        # set the values from the report if not s et automatically
        self.logger = testcaseSettings.get('LOGGER')
        Data = []

        try:
            self.logger.info('=================Running Testcase: {testcase} ============'.format(testcase=testcaseSettings["NAME"]))
            reports = self.gempypMethodExecutor(cls, testcaseSettings, **kwargs)

            # will never enter this  block
            if reports is None:
                reports = testcaseReporter(kwargs["PROJECTNAME"], testcaseSettings["NAME"])
                self.logger.error("Report object was not returned from the testcase file")
                reports.addRow("Exception Occured", "Exception occured in testcase: Report was not generated.", status.FAIL)    
        except Exception:
            etype, value, tb = sys.exc_info()
            self.logger.error(traceback.format_exc())
            info, error = traceback.format_exception(etype, value, tb)[-2:]
            reports = testcaseReporter(kwargs["PROJECTNAME"], testcaseSettings["NAME"])
            reports.addRow("Exception Occured", str(error) + 'at' + str(info), status.FAIL)

        if isinstance(reports, testcaseReporter):
            reports = [reports]

        for index, report in enumerate(reports):
            if not report.projectName:
                report.projectName = testcaseSettings.get("PROJECTNAME", "GEMPYP")

            if not report.testcaseName:
                report.testcaseName = testcaseSettings.get("NAME", "TESTCASE")
                report.testcaseName = f"{self.testcaseName}_{index}"

            # call the destructor if not already called.
            report.finalize_report()
            # if user has not provided its own resultfile
            if not report.resultFileName:
                report.jsonData = report.templateData.makeReport(
                    kwargs.get(
                        "OUTPUT_FOLDER", DefaultSettings.DEFAULT_GEMPYP_FOLDER
                    ), testcaseSettings["NAME"])
            result = report.serialize()
            Data.append(result)

        return Data
