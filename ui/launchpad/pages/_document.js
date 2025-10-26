import { Html, Head, Main, NextScript } from 'next/document'

export default function Document() {
  return (
    <Html lang="en" className="dark">
      <Head>
        <link rel="icon" href="/atom-favicon.svg" />
        <meta name="description" content="ATOM Cloud - Neural-powered autonomous cloud platform" />
      </Head>
      <body>
        <Main />
        <NextScript />
      </body>
    </Html>
  )
}