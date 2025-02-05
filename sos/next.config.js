const nextConfig = {
  reactStrictMode: true,

  // Configure rewrites based on environment
  async rewrites() {
    return {
      beforeFiles: [
        {
          source: "/api/:path*",
          destination: "http://backend:8000/:path*",
        },
      ],
    };
  },

  // Configure headers for development CORS
  // async headers() {
  //   return process.env.NODE_ENV === "development"
  //     ? [
  //         {
  //           source: "/api/:path*",
  //           headers: [
  //             { key: "Access-Control-Allow-Credentials", value: "true" },
  //             { key: "Access-Control-Allow-Origin", value: "*" },
  //             {
  //               key: "Access-Control-Allow-Methods",
  //               value: "GET,DELETE,PATCH,POST,PUT",
  //             },
  //             {
  //               key: "Access-Control-Allow-Headers",
  //               value:
  //                 "Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date",
  //             },
  //           ],
  //         },
  //       ]
  //     : [];
  // },

  // // Configure webpack for development
  // webpack: (config, { dev, isServer }) => {
  //   if (dev && !isServer) {
  //     // Enable source maps in development
  //     config.devtool = "eval-source-map";
  //   }
  //   return config;
  // },
};

module.exports = nextConfig;
