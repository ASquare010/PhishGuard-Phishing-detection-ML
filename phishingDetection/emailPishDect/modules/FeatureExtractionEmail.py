import email
import pandas as pd
import numpy as np
import re  


class FeatureExtractionEmail:

    df = pd.DataFrame()

    def __init__(self,emaill):
        final_features_list = []
        
        initial_features_list = ["from", "message-id", 'return-path', 'reply-to', 'errors-to', 'in-reply-to', 'references',
                                'to', 'cc', 'sender', 'dkim', 'dmarc', 'spf']


        def parse_email_header(email_content):
            # Parse the email content
            msg = email.message_from_string(email_content)

            # Initialize dictionary to store the parsed data
            email_data = {
                'From': [],
                'Message-ID': [],
                'Return-Path': [],
                'Reply-To': [],
                'Errors-To': [],
                'In-Reply-To': [],
                'References': [],
                'To': [],
                'CC': [],
                'Sender': [],
                'DKIM': [],  # Add 'DKIM' key
                'SPF': [],   # Add 'SPF' key
                'DMARC': [],  # Add 'DMARC' key
                'num_hops': []  # Add 'num_hops' key
            }

            # Define the list of header fields to extract
            header_fields = [
                'From',
                'Message-ID',
                'Return-Path',
                'Reply-To',
                'Errors-To',
                'In-Reply-To',
                'References',
                'To',
                'CC',
                'Sender'
            ]

            # Extract header information
            for field in header_fields:
                email_data[field].append(msg.get(field, ''))

            # Handle 'Received' headers
            received_headers = msg.get_all('Received')
            if received_headers:
                email_data['num_hops'] = [len(received_headers)]
                email_data['first_received'] = [received_headers[0]]
                for i, received in enumerate(received_headers[1:], start=2):
                    email_data[f'Received{i}'] = [received]
                email_data['last_received'] = [received_headers[-1]]
            else:
                email_data['num_hops'] = [0]
                email_data['first_received'] = ['']
                email_data['last_received'] = ['']

            # Parse Authentication-Results if present
            auth_results = msg.get('Authentication-Results')
            if auth_results:
                # Extract DKIM, SPF, and DMARC results
                dkim = re.search(r'dkim=(\w+)', auth_results)
                spf = re.search(r'spf=(\w+)', auth_results)
                dmarc = re.search(r'dmarc=(\w+)', auth_results)

                email_data['DKIM'].append(dkim.group(1) if dkim else np.nan)
                email_data['SPF'].append(spf.group(1) if spf else np.nan)
                email_data['DMARC'].append(dmarc.group(1) if dmarc else np.nan)
            else:
                # Append '' if Authentication-Results is not found
                email_data['DKIM'].append('')
                email_data['SPF'].append('')
                email_data['DMARC'].append('')


            # Create a DataFrame from the parsed data
            df = pd.DataFrame.from_dict(email_data, orient='index').transpose()

            return df
        
        df = parse_email_header(emaill) 
        
        df.columns = df.columns.str.lower()
        missing_feature_names = []
        final_features_list = []

        for name in initial_features_list:
            missing_feature_names.append('missing_' + name)

        for feature, name in zip(initial_features_list, missing_feature_names):
            df.loc[df[feature].isnull(), name] = 1
            df.loc[~df[feature].isnull(), name] = 0
            # Convert the columns to integers
            df[name] = df[name].astype(int)


        final_features_list.extend(missing_feature_names)
    
        # Append 'num_hops' to the final feature list
        final_features_list.append('num_hops')
        df['num_recipients_to'] = df.apply(lambda x: len(re.findall(
        r'([a-zA-Z0-9+._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', x['to'])), axis=1)

        df['num_recipients_cc'] = df.apply(lambda x: len(re.findall(
            r'([a-zA-Z0-9+._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', x['cc'])), axis=1)

        df['num_recipients_from'] = df.apply(lambda x: len(re.findall(
            r'([a-zA-Z0-9+._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', x['from'])), axis=1)

        final_features_list.append('num_recipients_to')
        final_features_list.append('num_recipients_cc')
        final_features_list.append('num_recipients_from')
        # Convert all column names to lowercase

        df = df.replace(np.nan, '', regex=True)

        emails_from = df.apply(self.extract_emails, col_name='from', axis=1)
        emails_message_id = df.apply(self.extract_emails, col_name='message-id', axis=1)
        emails_return_path = df.apply(self.extract_emails, col_name='return-path', axis=1)
        emails_reply_to = df.apply(self.extract_emails, col_name='reply-to', axis=1)
        emails_errors_to = df.apply(self.extract_emails, col_name='errors-to', axis=1)
        emails_in_reply_to = df.apply(self.extract_emails, col_name='in-reply-to', axis=1)
        emails_references = df.apply(self.extract_emails, col_name='references', axis=1)
        emails_to = df.apply(self.extract_emails, col_name='to', axis=1)
        emails_cc = df.apply(self.extract_emails, col_name='cc', axis=1)
        emails_sender = df.apply(self.extract_emails, col_name='sender', axis=1)

        #simScores = domains_df[['return', 'from']].apply(lambda x: simScore(*x), axis=1)
        #df['SimScore_return_from'] = simScores
        emails_df = pd.concat([emails_from, emails_message_id, emails_return_path, 
                        emails_errors_to, emails_reply_to, emails_in_reply_to, 
                        emails_references, emails_to, emails_cc, emails_sender], axis=1)

        # Set new column names
        emails_df = emails_df.set_axis(['from', 'message-id', 'return-path', 'errors-to', 'reply-to',
                                        'in-reply-to', 'references', 'to', 'cc', 'sender'], axis=1)
        
        emails_to_check = [('from', 'reply-to')]

        for val in emails_to_check:
            first_field = val[0]
            second_field = val[1]
            new_col_name = 'email_match_' + first_field + '_' + second_field

            df[new_col_name] = emails_df.apply(self.email_same_check, first_col=first_field, 
                            second_col=second_field, axis=1)
            final_features_list.append(new_col_name)
        
        domains_from = emails_df.apply(self.extract_domains, col_name='from', axis=1)
        domains_message_id = emails_df.apply(self.extract_domains, col_name='message-id', axis=1)
        domains_return_path = emails_df.apply(self.extract_domains, col_name='return-path', axis=1)
        domains_reply_to = emails_df.apply(self.extract_domains, col_name='reply-to', axis=1)
        domains_errors_to = emails_df.apply(self.extract_domains, col_name='errors-to', axis=1)
        domains_in_reply_to = emails_df.apply(self.extract_domains, col_name='in-reply-to', axis=1)
        domains_references = emails_df.apply(self.extract_domains, col_name='references', axis=1)
        domains_to = emails_df.apply(self.extract_domains, col_name='to', axis=1)
        domains_cc = emails_df.apply(self.extract_domains, col_name='cc', axis=1)
        domains_sender = emails_df.apply(self.extract_domains, col_name='sender', axis=1)


        domains_df = pd.concat([domains_from, domains_message_id, domains_return_path, 
                            domains_errors_to, domains_reply_to, domains_in_reply_to, 
                            domains_references, domains_to, domains_cc, domains_sender], axis=1)

        # Set new column names and assign the result back to domains_df
        domains_df = domains_df.set_axis(['from_domains', 'message-id_domains', 'return-path_domains', 'errors-to_domains', 'reply-to_domains',
                                        'in-reply-to_domains', 'references_domains', 'to_domains', 'cc_domains', 'sender_domains'], axis=1)

        # Concatenate the original dataframe with the domains dataframe
        df = pd.concat([df, domains_df], axis=1)
        df['domain_val_message-id'] = domains_df.apply(self.extract_domain_message_id, axis=1)
        df['domain_val_message-id'].value_counts()
            
        df.loc[~df['domain_val_message-id'].astype(str).str.contains('uwaterloo.ca'), 'domain_val_message-id'] = 0
        df.loc[df['domain_val_message-id'].astype(str).str.contains('uwaterloo.ca'), 'domain_val_message-id'] = 1

        df['domain_val_message-id'].value_counts()
        final_features_list.append('domain_val_message-id')


        domain_fields_to_check = [('message-id_domains', 'from_domains'), ('from_domains', 'return-path_domains'), ('message-id_domains', 'return-path_domains'), ('message-id_domains', 'sender_domains'), ('message-id_domains', 'reply-to_domains'),
                                ('return-path_domains', 'reply-to_domains'), ('reply-to_domains', 'to_domains'), ('to_domains', 'in-reply-to_domains'), ('errors-to_domains', 'message-id_domains'), ('errors-to_domains', 'from_domains'), ('errors-to_domains', 'sender_domains'),
                                ('errors-to_domains', 'reply-to_domains'), ('sender_domains', 'from_domains'), ('references_domains', 'reply-to_domains'), ('references_domains', 'in-reply-to_domains'), ('references_domains', 'to_domains'), ('from_domains', 'reply-to_domains'),
                                ('to_domains', 'from_domains'), ('to_domains', 'message-id_domains')]


        for val in domain_fields_to_check:
            first_field = val[0].replace('_domains', '')
            second_field = val[1].replace('_domains', '')
            new_col_name = 'domain_match_' + first_field + '_' + second_field 

            df[new_col_name] = domains_df.apply(self.domain_match_check, first_col = val[0], 
                                        second_col= val[1], axis=1)
            final_features_list.append(new_col_name)

        
        parser = ReceivedParser()

        # df.head(5)
        # df['domain_match_message-id_from']
        def get_for_domain_last_received(row):
            last_received_val = row['last_received']
            parsed_val = parser.parse(last_received_val)

            if self.check_if_valid(parsed_val, 'envelope_for'):
                main_domain = parsed_val['envelope_for'].split('@')[-1]
                main_domain_parts = main_domain.split('.')[-2:]

                # Check if there are at least two elements in main_domain_parts
                if len(main_domain_parts) >= 2:
                    main_domain = main_domain_parts[0] + '.' + re.sub('\W+', '', main_domain_parts[1])
                else:
                    main_domain = 'NA'

                return main_domain.lower()

            else:
                return 'NA'
        def check_for_received_domain_equal(row, field_name):
            field_vals = row[field_name]

            for item in field_vals:
                if item == get_for_domain_last_received(row):
                    return 1
            return 0
        
        df['domain_match_to_received'] = df.apply(check_for_received_domain_equal, field_name='to_domains', axis=1)
        df['domain_match_to_received'].value_counts()

        df['domain_match_reply-to_received'] = df.apply(check_for_received_domain_equal, field_name='reply-to_domains', axis=1)
        df['domain_match_reply-to_received'].value_counts()

        final_features_list.extend(['domain_match_reply-to_received', 'domain_match_to_received'])

        

        df_filtered = df[final_features_list]
        
        # arr = df_filtered.values
        
        self.df = df_filtered
    

    def domain_match_check(self,row, first_col, second_col): 
        first_domain_list = row[first_col]
        second_domain_list = row[second_col]

        if len(first_domain_list) == 0 or len(second_domain_list) == 0:
            return 0
        else:
            for d1 in first_domain_list:
                for d2 in second_domain_list: 
                    if d1 == d2:
                        return 1
            return 0
    
    def extract_domain_message_id(self,row):
        val = row['message-id_domains']
        if len(val) == 0:
            return ''
        else:
            return val[0]

    def extract_domains(self,row, col_name):
        emails_list = row[col_name]

        if len(emails_list) == 0:
            return []
        else:
            domains_list = []
            for email in emails_list:
                if len(email.split('.')) < 2:
                    continue
                else:
                    main_domain = email.split('@')[-1]
                    main_domain = main_domain.split('.')[-2:]
                    main_domain = main_domain[0] + '.' + re.sub('\W+','', main_domain[1])
                    domains_list.append(main_domain.lower())
            return domains_list
  

    def email_same_check(self,row, first_col, second_col):
        vals1 = row[first_col]
        vals2 = row[second_col]

        for val1 in vals1:
            for val2 in vals2:
                if val1 == val2:
                    return 1
        return 0
    def check_if_valid(self,dict_to_check, str_val):
        if dict_to_check is None:
            return False
        elif str_val not in dict_to_check:
            return False
        elif dict_to_check[str_val] is None:
            return False
        else:
            return True

        # emails in brackets '<>' are matched first, and if none, then other emails are matched
    def extract_emails(self,row, col_name):

        in_brackets = re.findall(r'<([a-zA-Z0-9+._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)>', row[col_name])

        if len(in_brackets) == 0:
            not_in_brackets = re.findall(r'([a-zA-Z0-9+._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', row[col_name])
            if len(not_in_brackets) == 0:
                return []
            else:
                return not_in_brackets
        else:
            return in_brackets




class ReceivedParser(object):
    regexes = [
        ("from\s+(mail\s+pickup\s+service|(?P<from_name>[\[\]\w\.\-]*))\s*(\(\s*\[?(?P<from_ip>[a-f\d\.\:]+)(\%\d+|)\]?\s*\)|)\s*by\s*(?P<by_hostname>[\w\.\-]+)\s*(\(\s*\[?(?P<by_ip>[\d\.\:a-f]+)(\%\d+|)\]?\)|)\s*(over\s+TLS\s+secured\s+channel|)\s*with\s*(mapi|Microsoft\s+SMTP\s+Server|Microsoft\s+SMTPSVC(\((?P<server_version>[\d\.]+)\)|))\s*(\((TLS|version=(?P<tls>[\w\.]+)|)\,?\s*(cipher=(?P<cipher>[\w\_]+)|)\)|)\s*(id\s+(?P<id>[\d\.]+)|)", "MS SMTP Server"), #exchange
        ("(from\s+(?P<from_name>[\[\S\]]+)\s+\(((?P<from_hostname>[\S]*)|)\s*\[(IPv6\:(?P<from_ipv6>[a-f\d\:]+)\:|)((?P<from_ip>[\d\.\:]+)|)\]\s*(\(may\s+be\s+forged\)|)\)\s*(\(using\s+(?P<tls>[\w\.]+)\s+with\s+cipher\s+(?P<cipher>[\w\-]+)\s+\([\w\/\s]+\)\)\s+(\(No\s+client\s+certificate\s+requested\)|)|)|)\s*(\(Authenticated\s+sender\:\s+(?P<authenticated_sender>[\w\.\-\@]+)\)|)\s*by\s+(?P<by_hostname>[\S]+)\s*(\((?P<by_hostname2>[\S]*)\s*\[((?P<by_ipv6>[a-f\:\d]+)|)(?P<by_ip>[\d\.]+)\]\)|)\s*(\([^\)]*\)|)\s*(\(Postfix\)|)\s*(with\s+(?P<protocol>\w*)|)\s*id\s+(?P<id>[\w\-]+)\s*(for\s+\<(?P<envelope_for>[\w\.\@]+)\>|)", "postfix"), #postfix
        ("(from\s+(?P<from_name>[\[\S\]]+)\s+\(((?P<from_hostname>[\S]*)|)\s*\[(IPv6\:(?P<from_ipv6>[a-f\d\:]+)|)\]\)\s*(\(using\s+(?P<tls>[\w\.]+)\s+with\s+cipher\s+(?P<cipher>[\w\-]+)\s+\([\w\/\s]+\)\)\s+(\(No\s+client\s+certificate\s+requested\)|)|)|)\s*(\(Authenticated\s+sender\:\s+(?P<authenticated_sender>[\w\.\-\@]+)\)|)\s*by\s+(?P<by_hostname>[\S]+)\s*(\((?P<by_hostname2>[\S]*)\s*\[((?P<by_ipv6>[a-f\:\d]+)|)(?P<by_ip>[\d\.]+)\]\)|)\s*(\([^\)]*\)|)\s*(\(Postfix\)|)\s*(with\s+(?P<protocol>\w+)|)\s*id\s+(?P<id>[\w\-]+)\s*(for\s+\<(?P<envelope_for>[\w\.\@]+)\>|)", "postfix"),#POSTFIX
        ("\s*from\s+\[?(?P<from_ip>[\d\.\:]+)\]?\s*(\((port=\d+|)\s*helo=(?P<from_name>[\[\]\w\.\:\-]+)\)|)\s+by\s+(?P<by_hostname>[\w\-\.]+)\s+with\s+(?P<protocol>\w+)\s*(\((?P<cipher>[\w\.\:\_\-]+)\)|)\s*(\(Exim\s+(?P<exim_version>[\d\.\_]+)\)|)\s*\(envelope-from\s+<?(?P<envelope_from>[\w\@\-\.]*)>?\s*\)\s*id\s+(?P<id>[\w\-]+)\s*\s*(for\s+<?(?P<envelope_for>[\w\.\@]+)>?|)", "exim"), #exim
        ("\s*from\s+(?P<from_hostname>[\w\.]+)\s+\(\[?(?P<from_ip>[\d\.\:a-f]+)\]?(\:\d+|)\s*(helo\=\[?(?P<from_name>[\w\.\:\-]+)|)\]?\)\s+by\s+(?P<by_hostname>[\w\-\.]+)\s+with\s+(?P<protocol>\w+)\s+(\((?P<cipher>[\w\.\:\_]+)\)|)\s*\(Exim\s+(?P<exim_version>[\d\.\_]+)\)\s*\(envelope-from\s+\<(?P<envelope_from>[\w\@\-\.]+)\>\s*\)\s*id\s+(?P<id>[\w\-]+)\s*(for\s+(?P<envelope_for>[\w\.\@]+)|)", "exim"),# exim
        ("from\s+(?P<from_name>[\w\.\-]+)\s+by\s+(?P<by_hostname>[\w\.\-]+)\s+with\s+(?P<protocol>\w+)\s+\(Exim\s+(?P<version>[\d\.]+)\)\s+\(envelope-from\s+<*(?P<envelope_from>[\w\.\-\@]+)>*\)\s+id\s+(?P<id>[\w\.\-]+)\s+for\s+<?(?P<envelope_for>[\w\.\-\@]+)>?", "exim"), #exim
        ("from\s+(?P<from_name>[\[\]\w\-\.]+)\s+\(((?P<from_hostname>[\w\.\-]+)|)\s*\[(?P<from_ip>[\da-f\.\:]+)\]\)\s+by\s+(?P<by_hostname>[\w\.\-]+)\s+\(Oracle\s+Communications\s+Messaging\s+Server\s+(?P<oracle_version>[\w\.\-]+)(\([\d\.]+\)|)\s+(32bit|64bit|)\s*(\([^\)]+\)|)\)\s*with\s+(?P<protocol>\w+)\s+id\s+\<?(?P<id>[\w\@\.\-]+)\>?", "Oracle Communication Messaging Server"), #Oracle
        ("from\s+(?P<from_hostname>[\w\-\.]+)\s+\(\[(?P<from_ip>[\d\.\:a-f]+)\]\s+helo=(?P<from_name>[\w\.\-]+)\)\s+by\s+(?P<by_hostname>[\w\.\-]+)\s+with\s+(?P<protocol>\w+)\s+\(ASSP\s+(?P<assp_version>[\d\.]+)\s*\)", "ASSP"), #ASSP
        ("from\s+(?P<from_hostname>[\[\]\d\w\.\-]+)\s+\(\[\[?(?P<from_ip>[\d\.]+)(\:\d+|)\]\s*(helo=(?P<from_name>[\w\.\-]+)|)\s*\)\s+by\s+(?P<by_hostname>[\w\.\-]+)\s+\(envelope-from\s+\<?(?P<envelope_from>[^>]+)\>?\)\s+\(ecelerity\s+(?P<version>[\d\.]+)\s+r\([\w\-\:\.]+\)\)\s+with\s+(?P<protocol>\w+)\s*(\(cipher=(?P<cipher>[\w\-\_]+)\)|)\s*id\s+(?P<id>[\.\-\w\/]+)", "ecelerity"), #ecelerity
        ("from\s+(?P<from_name>[\[\]\w\.\-]+)\s+\(((?P<from_hostname>[\w\.\-]+)|)\s*(\[(?P<from_ip>[\d\.\:a-f]+)\]|)\)\s*by\s+(?P<by_hostname>[\w\.\-]+)\s+(\([\w\.\-\=]+\)|)\s+with\s+(?P<protocol>\w+)\s+\(Nemesis\)\s+id\s+(?P<id>[\w\.\-]+)\s*(for\s+\<?(?P<envelope_for>[\w\.\@\-]+)\>?|)", "nemesis"), #nemesis
        ("\(qmail\s+\d+\s+invoked\s+(from\s+network|)(by\s+uid\s+\d+|)\)", "qmail"), #WTF qmail
        ("from\s+\[?(?P<from_ip>[\d\.a-f\:]+)\]?\s+\(account\s+<?(?P<envelope_from>[\w\.\@\-]+)>?\s+HELO\s+(?P<from_name>[\w\.\-]+)\)\s+by\s+(?P<by_hostname>[\w\.\-]*)\s+\(CommuniGate\s+Pro\s+SMTP\s+(?P<version>[\d\.]+)\)\s+with\s+(?P<protocol>\w+)\s+id\s+(?P<id>[\w\-\.]+)\s+for\s+<?(?P<envelope_for>[\w\.\-\@]+)>?", "CommuniGate"), #CommuniGate
        ("from\s+(?P<from_ip>[\d\.\:a-f]+)\s+\(SquirrelMail\s+authenticated\s+user\s+(?P<envelope_from>[\w\@\.\-]+)\)\s+by\s+(?P<by_hostname>[\w\.\-]+)\s+with\s+(?P<protocol>\w+)", "SquirrelMail"),
        ("by\s+(?P<by_hostname>[\w\.\-]+)\s+\((?P<protocol>\w+)\s+sendmail\s*(emulation|)\)", "sendmail"), #sendmail
        ("from\s+(?P<from_name>[\[\]\w\.\-]+)\s+\(\[(?P<from_hostname>[\w\.\-]+)\]\s+\[(?P<from_ip>[\d\.a-f\:]+)\]\)\s+by\s+(?P<by_hostname>[\w\.\-]+)\s+\(Sun\s+Java\(tm\)\s+System\s+Messaging\s+Server\s+(?P<version>[\w\.\-]+)\s+\d+bit\s+\(built\s+\w+\s+\d+\s+\d+\)\)\s+with\s+(?P<protocol>\w+)\s+id\s+<?(?P<id>[\w\.\-\@]+)>?", "Sun Java System Messaging Server"), # Sun Java System Messaging Server
        ("from\s+(?P<from_name>[\w\.\-\[\]]+)\s+\((?P<from_ip>[\d\.a-f\:]+)\)\s+by\s+(?P<by_hostname>[\w\.\-]+)\s+\(Axigen\)\s+with\s+(?P<protocol>\w+)\s+id\s+(?P<id>[\w\.\-]+)", "Axigen"), #axigen
        ("from\s+(?P<from_name>[\w\.\-]+)\s+\((?P<from_hostname>[\w\.\-]+)\s+\[(?P<from_ip>[\d\.a-f\:]+)\]\)\s+by\s+(?P<by_hostname>[\w\.\-]+)\s+\(Horde\s+MIME\s+library\)\s+with\s+(?P<protocol>\w+)", "Horde MIME library"), #Horde
        ("from\s+(?P<from_name>[\w\.\-\[\]]+)\s+by\s+(?P<by_hostname>[\w\.\-]+)\s+\(PGP\s+Universal\s+Service\)", "PGP Universal Service", "local"), # PGP Universal Service
        ("from\s+(?P<from_name>[\w\.\-]+)\s+by\s+(?P<by_hostname>[\w\.\-]+)\s+with\s+(?P<protocol>\w+)\s+\(Sophos\s+PureMessage\s+Version\s+(?P<version>[\d\.\-]+)\)\s+id\s+(?P<id>[\w\.\-]+)\s+for\s+(?P<envelope_for>[\w\.\-\@]+)", "Sophos PureMessage"), #Sophos PureMessage
        ("by\s+(?P<by_ip>[\d\.\:a-f]+)\s+with\s+(?P<protocol>\w+)", "unknown"), # other
        ("from\s+(?P<from_name>[\w\.\-]+)\s+\#?\s*(\(|\[|\(\[)\s*(?P<from_ip>[\d\.\:a-f]+)\s*(\]|\)|\]\))\s+by\s+(?P<by_hostname>[\w\.\-]+)(\s+\([\w\.\s\/]+\)|)\s*(with\s+(?P<protocol>\w+)|)\s*(id\s+(?P<id>[\w]+)|)(\(\-\)|)\s*(for\s+\<(?P<envelope_for>[\w\@\.]+)\>?|)", "unknown"), #unknown
        ("from\s+(?P<from_hostname>[\w\.\-]+)\s*\(HELO\s+(?P<from_name>[\w\.\-]+)\)\s*\(\[?(?P<from_ip>[\d\.\:a-f]+)\]?\)\s+by\s+(?P<by_hostname>[\w\.\-]+)(\s+\([\d\.]+\)|)\s*(with\s+(?P<protocol>\w+)|)\s*(id\s+(?P<id>[\w]+)|)(\(\-\)|)", "unknown"), #other other
        ("from\s+([\(\[](?P<from_ip>[\d\.\:a-f]+)[\)\]]|)\s+by\s+(?P<by_hostname>[\w\.\-]+)\s+id\s+(?P<id>\w+)\s*(with\s+(?P<protocol>\w+)|)\s*\s*(for\s+\<(?P<envelope_for>[\w\@\.\-]+)\>|)", "unknown"),#other
        ("from\s+(?P<from_hostname>[\w\.]+)\s+(\(HELO\s+(?P<from_name>[\w\.\-]+)\)|)\s*(\((?P<from_ip>[\da-f\.\:]+)\)|)\s*by\s+(?P<by_hostname>[\w\.\-]+)\s+with\s+(?P<cipher>[\w\-]+)\s+encrypted\s+SMTP", "unknown"), #unknown
        ("from\s+(?P<from_hostname>[\w\.\-]+)\s+(\(HELO\s+(?P<from_name>[\w\.\-]+)\)|)\s+\((?P<envelope_from>[\w\.]+\@[\w\.]+)\@(?P<from_ip>[\da-d\.\:]+)\)\s+by\s+(?P<by_hostname>[\w\.\-]+)\s+with\s+(?P<protocol>\w+)", "unknown"), #unknown
        ("from\s+(?P<from_hostname>[\w\.\-]+)\s+\(HELO\s+(?P<from_name>[\w\.\-\?]+)\)\s+\(\w+\@[\w\.]+\@(?P<from_ip>[\d\.a-f\-]+)_\w+\)\s+by\s+(?P<by_hostname>[\w\.\-\:]+)\s+with\s+(?P<protocol>\w+)", "unknown"), #unknown
        ("from\s+(?P<from_name>[\w\.\-\[\]]+)\s+\(\[(?P<from_ip>[\da-f\.\:]+)\]\)\s+by\s+(?P<by_hostname>[\w\.\-]+)\s+\(\[(?P<by_ip>[\d\.a-f\:]+)\]\)\s+with\s+(?P<protocol>\w+)", "unknown"), #unknown
        ]
    @staticmethod
    def parse(header):
        parts = header.split(";")
        if len(parts) != 2:
            return None

        data = {}

        # parse the hard part
        found = False
        for regex in ReceivedParser.regexes:
            match = re.match(regex[0], parts[0], re.IGNORECASE)
            if match:
                data['server'] = regex[1]
                found = True
                break

        if not found:
            return None
        return {**data, **match.groupdict()}