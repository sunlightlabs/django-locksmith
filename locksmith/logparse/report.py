import re, os, datetime, gzip
from locksmith.common import apicall

def submit_report(log_path, log_regex, log_date_format, log_date, log_custom_transform, locksmith_api_name, locksmith_signing_key, locksmith_endpoint):
    log_re = re.compile(log_regex)
    
    log_directory = os.path.dirname(log_path)
    log_file_re = re.compile(re.escape(os.path.basename(log_path)).replace(r'\*', '.*'))
    
    # only include the ones that match our wildcard pattern
    unsorted_log_files = [file for file in os.listdir(log_directory) if log_file_re.match(file)]
    
    # do some voodoo to make sure they're in the right order, since the numbers may be lexicographically sorted in an odd way
    number_re = re.compile(r'\d+')
    log_files = sorted(unsorted_log_files, key=lambda f: int(number_re.findall(f)[0]) if number_re.search(f) else -1)
    
    totals = {}
    
    # loop over the files
    last_loop = False
    for log_file in log_files:
        if log_file.endswith('.gz'):
            file = gzip.open(os.path.join(log_directory, log_file), 'rb')
        else:
            file = open(os.path.join(log_directory, log_file), 'r')
        
        # loop over the rows
        for row in file:
            match = log_re.match(row)
            if match:
                record = match.groupdict()
                day = datetime.datetime.strptime(record['date'], log_date_format).date()
                if day == log_date and record['status'] == '200' and record['apikey'] and record['apikey'] != '-':
                    # normalize the endpoint
                    endpoint = log_custom_transform(record['endpoint']) if log_custom_transform else record['endpoint']
                    
                    # add it to the tally
                    if record['apikey'] not in totals:
                        totals[record['apikey']] = {}
                    
                    if endpoint not in totals[record['apikey']]:
                        totals[record['apikey']][endpoint] = 1
                    else:
                        totals[record['apikey']][endpoint] += 1
                elif day < log_date:
                    # this is the last log we need to parse
                    last_loop = True
        if last_loop:
            break
    
    # submit totals to hub
    submit_date = log_date.strftime('%Y-%m-%d')
    total_submitted = 0
    for api_key in totals:
        for endpoint in totals[api_key]:
            apicall(
                locksmith_endpoint,
                locksmith_signing_key,
                api = locksmith_api_name,
                date = submit_date,
                endpoint = endpoint,
                key = api_key,
                calls = totals[api_key][endpoint]
            )
            total_submitted += totals[api_key][endpoint]
    return total_submitted
