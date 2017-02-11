# get_chromium_issue_data.py issue path-to-depot-tools
#
# This script returns the json data for a given issue number.
# Return codes:
#  0 -- All good, stdout should include json info corresponding to the issue.
#  1 -- Fatal error. Not sure what to do
#  2 -- Error. stdout can include message to user.
#

if __name__ == '__main__':
  import sys

  issue = sys.argv[1]
  if issue.isdigit() is not True:
    print("Bad issue number")
    exit(1);

  sys.path = sys.path + [sys.argv[2]]

  import auth
  from third_party import httplib2

  authenticator = auth.get_authenticator_for_host("bugs.chromium.org", auth.make_auth_config())
  http = authenticator.authorize(httplib2.Http())
  url = ("https://monorail-prod.appspot.com/_ah/api/monorail/v1/projects/chromium/issues/%s") % issue

  try:
    _, body = http.request(url)
  except auth.LoginRequiredError:
    print("Not logged in. Run: depot-tools-auth login bugs.chromium.org")
    exit(2)

  print(body)
  exit(0)
