from insightsoncode.ioc_wrappers import log_constantpoints, log_codepoint
from time import sleep

def example():
    log_endpoint = log_constantpoints(csv_filename = "sample.csv", 
                                    project_id = "1", branch_id = "1", customer_id = "5")
    log_codepoint = log_codepoint
    

    @log_codepoint(code_id = "2", code_cost = 300)
    def common_function_a(ioc_logger):
        sleep(1)


    @log_endpoint(endpoint_id = "1")
    def endpoint1(ioc_logger, *args, **kwargs): # or ioc_node_id
        common_function_a()

if __name__ == "__main__":
    example()