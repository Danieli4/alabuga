/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  reactStrictMode: true,
  compiler: {
    styledComponents: true
  },
  experimental: {
    serverComponentsExternalPackages: ['@reduxjs/toolkit']
  }
};

export default nextConfig;
