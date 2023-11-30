/**
 * Takes a cookie string
 * @param {String} cookieString - The cookie string value: "val=key; val2=key2; val3=key3;"
 * @param {String} key - The name of the cookie we are reading from the cookie string
 * @returns {(String|null)} Returns the value of the cookie OR null if nothing was found.
 */
function getCookie(cookieString, key) {
  if (cookieString) {
    const allCookies = cookieString.split("; ")
    const targetCookie = allCookies.find(cookie => cookie.includes(key))
    if (targetCookie) {
      const [_, value] = targetCookie.split("=")
      return value
    }
  }

  return null
}

addEventListener('fetch', event => {
    event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  let authToken="<B2_DOWNLOAD_TOKEN>"
  let b2Headers = new Headers(request.headers)

  const cookies = request.headers.get("Cookie");

  let tk = new URL(request.url).searchParams.get("token")

  if (!tk) {
    tk = getCookie(cookies, 'token');
  }

  if (!tk) return new Response('', {status: 401, statusText: 'unauthorized'})

  const verifyResponse = await fetch("https://auth.ezrahuang.com/verify", {
      method: 'POST',
      headers: {'content-type': 'application/x-www-form-urlencoded'},
      body: new URLSearchParams({token: tk}),
  }).then(res => res.json())
  if (!verifyResponse.valid) return new Response(new Blob(), {status: 401, statusText: 'unauthorized'})

  b2Headers.append("Authorization", authToken)
  let modRequest = new Request(request.url, {
      method: request.method,
      headers: b2Headers
  })
  const response = await fetch(modRequest)
  const newResponse = new Response(response.body, response);
  newResponse.headers.append("Access-Control-Allow-Origin", "*");
  return newResponse;
}
