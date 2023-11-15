addEventListener('fetch', event => {
    event.respondWith(handleRequest(event.request))
})

async function handleRequest(request) {
  let authToken="<B2_DOWNLOAD_TOKEN>"
  let b2Headers = new Headers(request.headers)

  const tk = new URL(request.url).searchParams.get('token')
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
