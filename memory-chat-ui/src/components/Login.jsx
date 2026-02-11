import React from "react";
import { GoogleLogin } from "@react-oauth/google";
import { jwtDecode } from "jwt-decode";

const Login = ({ setUser }) => {

  const handleSuccess = (credentialResponse) => {
    const decoded = jwtDecode(credentialResponse.credential);

    const user = {
      name: decoded.name,
      email: decoded.email,
      picture: decoded.picture,
      sub: decoded.sub
    };

    localStorage.setItem("user", JSON.stringify(user));
    setUser(user);
  };

  return (
    <div className="login-screen">
      <h2>Sign in to Memory Assistant</h2>
      <GoogleLogin
        onSuccess={handleSuccess}
        onError={() => console.log("Login Failed")}
      />
    </div>
  );
};

export default Login;
