import React from 'react'
import Head from 'next/head'
import AtomSidebar from './AtomSidebar'
import AtomTopbar from './AtomTopbar'
import AtomFooter from './AtomFooter'

interface AtomLayoutProps {
  children: React.ReactNode
  title?: string
}

export function AtomLayout({ children, title = 'ATOM Admin Console' }: AtomLayoutProps) {
  return (
    <>
      <Head>
        <title>{title}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>

      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex">
        <AtomSidebar />
        
        <div className="flex-1 flex flex-col">
          <AtomTopbar title={title} />
          
          <main className="flex-1 p-6">
            <div className="max-w-7xl mx-auto">
              {children}
            </div>
          </main>
          
          <AtomFooter />
        </div>
      </div>
    </>
  )
}

export default AtomLayout