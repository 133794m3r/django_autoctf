virtual_hosts = {
	"www.transcendental.us":"home_page.urls",
	"transcendental.us":"home_page.urls",
	"transcendental.local":"home_page.urls",
	"www.crimsonstrife.com":"ctf_club.urls",
	"crimsonstrife.com":"ctf_club.urls",
	"crimsonstrife.local":"ctf_club.urls",
}
class VirtualHostMiddleware:
	def __init__(self,get_response):
		self.get_response = get_response

	def __call__(self,request):
		host = request.get_host()
		request.urlconf = virtual_hosts.get(host)
		response = self.get_response(request)

		return response
