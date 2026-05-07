/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  basePath: '/jinwen-express',
  assetPrefix: '/jinwen-express',
  images: { unoptimized: true },
  trailingSlash: true,
};

module.exports = nextConfig;
