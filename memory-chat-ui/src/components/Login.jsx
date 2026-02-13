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
      
      {/* Animated background elements */}
      <div className="login-bg-orb orb-1"></div>
      <div className="login-bg-orb orb-2"></div>
      <div className="login-bg-orb orb-3"></div>
      
      {/* Login card */}
      <div className="login-card">
        
        {/* Icon/Logo */}
        <div className="login-icon">
          <div className="brain-icon">🧠</div>
        </div>
        
        {/* Title */}
        <h1 className="login-title">Memory Assistant</h1>
        
        {/* Subtitle */}
        <p className="login-subtitle">
          Your AI companion that remembers<br/>
          everything about your conversations
        </p>
        
        {/* Features list */}
        <div className="login-features">
          <div className="feature-item">
            <span className="feature-icon">💭</span>
            <span>Contextual conversations</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">🔒</span>
            <span>Secure & private</span>
          </div>
          <div className="feature-item">
            <span className="feature-icon">⚡</span>
            <span>Lightning fast responses</span>
          </div>
        </div>
        
        {/* Google Login Button */}
        <div className="login-button-wrapper">
          <GoogleLogin
            onSuccess={handleSuccess}
            onError={() => console.log("Login Failed")}
            theme="filled_black"
            size="large"
            text="continue_with"
            shape="rectangular"
          />
        </div>
        
        {/* Footer text */}
        <p className="login-footer">
          By continuing, you agree to our terms and privacy policy
        </p>
        
      </div>
      
    </div>
  );
};

export default Login;