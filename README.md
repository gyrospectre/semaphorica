tweetlist:
  checkpoint_provider: aws-ssm
  input:
    twitter:
      list_id: 1234567890123456789

  processors:

  outputs:
    - file:
        filename: test.txt
    - splunk:
        host: localhost:8089
        index: prod_test
        sourcetype: osint:twitter