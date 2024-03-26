from bs4 import BeautifulSoup
import pytest
from phishingDetection.urlPishDect.modules.PreProcess import PreProcessURLS
from datetime import datetime, timedelta
#chnaged email ,iframe, disableright click,  domain age and dns same


extractor = PreProcessURLS.PreProcessURLS()

# Test for getDomain method
def test_getDomain():
    # Case 1: Check domain stripping for domains starting with "www."
    extractor.domain = "www.example.com"
    assert extractor.getDomain() == "example.com", "Should strip 'www.' from domain"
    # Case 2: Check domain handling for domains not starting with "www."
    extractor.domain = "example.com"
    assert extractor.getDomain() == "example.com", "Should return the domain as is"


# Test for usingIp method
def test_usingIp():
    # Case 1: Domain is an IP address
    extractor.domain = "192.168.1.1"
    assert extractor.usingIp() == -1, "Should return -1 for an IP address"
    # Case 2: Domain is not an IP address
    extractor.domain = "example.com"
    assert extractor.usingIp() == 1, "Should return 1 for a non-IP address domain"


# Test for longUrl method
def test_longUrl():
    # Case 1: URL length < 54
    extractor.url = "http://example.com"
    assert extractor.longUrl() == 1, "Should return 1 for URL length < 54"
    # Case 2: URL length between 54 and 75
    extractor.url = "http://" + "example.com/" + "a" * 50
    assert extractor.longUrl() == 0, "Should return 0 for URL length between 54 and 75"
    # Case 3: URL length > 75
    extractor.url = "http://" + "example.com/" + "a" * 76
    assert extractor.longUrl() == -1, "Should return -1 for URL length > 75"


# Test for shortUrl method
def test_shortUrl():
    # Case 1: URL is a shortened URL
    extractor.url = "http://bit.ly/example"
    assert extractor.shortUrl() == -1, "Should return -1 for shortened URLs"
    # Case 2: URL is not a shortened URL
    extractor.url = "http://example.com"
    assert extractor.shortUrl() == 1, "Should return 1 for non-shortened URLs"


# Test for @ symbol method
def test_symbol():
    # Case 1: URL contains '@' symbol
    extractor.url = "http://example.com/@login"
    assert extractor.symbol() == -1, "Should return -1 if URL contains '@' symbol"
    # Case 2: URL does not contain '@' symbol
    extractor.url = "http://example.com"
    assert extractor.symbol() == 1, "Should return 1 if URL does not contain '@' symbol"


# Test for redirecting method
def test_redirecting():
    # Case 1: URL has no redirection '//'
    extractor.url = "http://example.com"
    assert extractor.redirecting() == 1, "Should return 1 if URL has no redirection '//'"
    # Case 2: URL has redirection '//'
    extractor.url = "http://example.com//redirect"
    assert extractor.redirecting() == -1, "Should return -1 if URL has redirection '//'"


# Test for prefixSuffix method
def test_prefixSuffix():
    # Case 1: Domain with a hyphen, expecting -1
    extractor.domain = "example-test.com"
    assert extractor.prefixSuffix() == -1, "Expected -1 for domains with hyphen"
    # Case 2: Domain without a hyphen, expecting 1
    extractor.domain = "example.com"
    assert extractor.prefixSuffix() == 1, "Expected 1 for domains without hyphen"


# Test for subDomains method
def test_subDomains():
    # Case 1: URL with one dot, expecting 1
    extractor.url = "http://example.com"
    assert extractor.subDomains() == 1, "Expected 1 for URLs with one dot"
    # Case 2: URL with two dots, expecting 0
    extractor.url = "http://sub.example.com"
    assert extractor.subDomains() == 0, "Expected 0 for URLs with two dots"


# Test for hppts method
def test_hppts():
    # Case 1: URL using HTTPS, expecting 1
    extractor.urlparse = type('', (), {})()  # Mocking urlparse result
    extractor.urlparse.scheme = "https"
    assert extractor.hppts() == 1, "Expected 1 for HTTPS URLs"
    # Case 2: URL not using HTTPS (e.g., HTTP), expecting -1
    extractor.urlparse.scheme = "http"
    assert extractor.hppts() == -1, "Expected -1 for non-HTTPS URLs"


# Test for domainRegLen method
def test_domainRegLen():
    # Case 1: Domain registered for more than 12 months, expecting 1
    one_year_ago = datetime.now() - timedelta(days=365)
    extractor.whois_response = type('', (), {})()  # Mocking whois response
    extractor.whois_response.expiration_date = datetime.now() + timedelta(days=365)
    extractor.whois_response.creation_date = one_year_ago
    assert extractor.domainRegLen() == 1, "Expected 1 for domains registered for more than 12 months"


# Test for anchorURL method
def test_anchorURL():
    # Case 1: Anchor tags pointing to the same domain, expecting 1
    extractor.soup = BeautifulSoup('<a href="http://example.com">Example</a>', 'html.parser')
    assert extractor.anchorURL() == 1, "Expected 1 when anchor tags point to the same domain"


# Test for hTTPSDomainURL method
def test_hTTPSDomainURL():
    # Case 1: Domain with HTTPS, expecting -1
    extractor.domain = "https://example.com"
    assert extractor.hTTPSDomainURL() == -1, "Expected -1 for domain with HTTPS"
    # Case 2: Domain without HTTPS, expecting 1
    extractor.domain = "http://example.com"
    assert extractor.hTTPSDomainURL() == 1, "Expected 1 for domain without HTTPS"


# Test for nonStdPort method
def test_nonStdPort():
    # Case 1: Domain without specified port, expecting 1
    extractor.domain = "example.com"
    assert extractor.nonStdPort() == 1, "Expected 1 for domain without specified port"
    # Case 2: Domain with specified port, expecting -1
    extractor.domain = "example.com:8080"
    assert extractor.nonStdPort() == -1, "Expected -1 for domain with specified port"


# Test for serverFormHandler method
def test_serverFormHandler():
    # Case 1: No form actions present
    extractor.soup = BeautifulSoup('<form></form>', 'html.parser')
    assert extractor.serverFormHandler() == 1, "Expected 1 when no form actions are present"
    # Case 2: Form action is external
    extractor.soup = BeautifulSoup('<form action="http://external.com/submit"></form>', 'html.parser')
    extractor.url = "http://example.com"
    extractor.domain = "example.com"
    assert extractor.serverFormHandler() == 0, "Expected 0 when form action is external"


# Test for infoEmail method
def test_infoEmail():
    # Case 1: HTML contains mail-related patterns, expecting -1
    html_content_with_mail = '<a href="mailto:test@example.com">Send Email</a>'
    extractor.soup = BeautifulSoup(html_content_with_mail, 'html.parser')
    assert extractor.infoEmail() == -1, "Expected -1 when HTML contains mail-related patterns"
    # Case 2: HTML does not contain mail-related patterns, expecting 1
    html_content_without_mail = '<a href="http://example.com">Visit Example</a>'
    extractor.soup = BeautifulSoup(html_content_without_mail, 'html.parser')
    assert extractor.infoEmail() == 1, "Expected 1 when HTML does not contain mail-related patterns"


# Test for abnormalURL method
def test_abnormalURL():
    # Case 1: Response text matches whois response, expecting 1
    extractor.response = type('', (), {})()  # Mocking response
    extractor.response.text = "Matching text"
    extractor.whois_response = "Matching text"
    assert extractor.abnormalURL() == 1, "Expected 1 when response text matches whois response"
    # Case 2: Response text does not match whois response, expecting -1
    extractor.response.text = "Different text"
    assert extractor.abnormalURL() == -1, "Expected -1 when response text does not match whois response"

# Test for websiteForwarding method
def test_websiteForwarding():
    # Case 1: No forwarding, expecting 1
    extractor.response = type('', (), {})()
    extractor.response.history = []
    assert extractor.websiteForwarding() == 1, "Expected 1 when there is no website forwarding"
    # Case 2: Multiple forwardings, expecting -1
    extractor.response.history = ['dummy'] * 5
    assert extractor.websiteForwarding() == -1, "Expected -1 when multiple forwardings are present"

# Test for statusBarCust method
def test_statusBarCust():
    # Case 1: Detects malicious script
    extractor.response.text ='<script>alert("Bad script") onmouseover="doBadThings()"</script>'
    assert extractor.statusBarCust() == 1, "Should detect malicious script and return 1"
    # Case 2: No malicious script detected
    extractor.response.text = '<div>No scripts here</div>'
    assert extractor.statusBarCust() == -1, "Should not find malicious script and return -1"

# Test for disableRightClick method
def test_disableRightClick():
    # Case 1: Page disables right-click, expecting 1
    extractor.response = type('', (), {})()  # Mocking response
    extractor.response.text = "document.addEventListener('contextmenu', event => event.preventDefault());"
    assert extractor.disableRightClick() == 1, "Expected 1 when page disables right-click"
    # Case 2: Page does not disable right-click, expecting -1
    extractor.response.text = "<html></html>"
    assert extractor.disableRightClick() == -1, "Expected -1 when page does not disable right-click"


# Test for usingPopupWindow method
def test_usingPopupWindow():
    # Case 1: Page uses popup window (alert), expecting 1
    extractor.response = type('', (), {})()  # Mocking response
    extractor.response.text = "alert('Hello World!');"
    assert extractor.usingPopupWindow() == 1, "Expected 1 when page uses popup window"
    # Case 2: Page does not use popup window, expecting -1
    extractor.response.text = "<html></html>"
    assert extractor.usingPopupWindow() == -1, "Expected -1 when page does not use popup window"


# Test for iframeRedirection method
def test_iframeRedirection():
    # Case 1: Page uses iframe for redirection, expecting 1
    extractor.response = type('', (), {})()  # Mocking response
    extractor.response.text = "<iframe src='http://example.com'></iframe>"
    assert extractor.iframeRedirection() == 1, "Expected 1 when page uses iframe for redirection"
    # Case 2: Page does not use iframe for redirection, expecting -1
    extractor.response.text = "<html></html>"
    assert extractor.iframeRedirection() == -1, "Expected -1 when page does not use iframe for redirection"


# Test for ageofDomain method
def test_ageofDomain():
    # Case 1: Domain age is more than 6 months, expecting 1
    six_months_ago = datetime.now() - timedelta(days=6*30)
    extractor.whois_response = type('', (), {})()  # Mocking whois_response
    extractor.whois_response.creation_date = six_months_ago
    assert extractor.ageofDomain() == 1, "Expected 1 when domain age is more than 6 months"
    # Case 2: The setup for a domain younger than 6 months would follow similarly, adjusting the `creation_date`
    recent_creation_date = datetime.now() - timedelta(days=30)  # Assuming the domain was created 30 days ago
    extractor.whois_response = type('', (), {})()  # Mocking whois_response
    extractor.whois_response.creation_date = recent_creation_date
    assert extractor.ageofDomain() == -1, "Expected -1 when domain age is less than 6 months"


# Test for getDepth method
def test_getDepth():
    # Case 1: Simulate URL with deep path, expecting depth > 1
    extractor.url = "http://example.com/path/to/resource"
    assert extractor.getDepth() > 1, "Expected depth > 1 for URL with deep path"
    # Case 2: Simulate root URL, expecting depth = 0
    extractor.url = "http://example.com"
    assert extractor.getDepth() == 0, "Expected depth = 0 for root URL"


