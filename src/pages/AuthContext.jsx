import React, { createContext, useContext, useState, useEffect } from "react";

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    // Пытаемся загрузить пользователя из localStorage
    const storedUser = localStorage.getItem("user");
    return storedUser ? JSON.parse(storedUser) : null;
  });

  
  // Функция для входа
  const login = (userData) => {
    setUser(userData);
    localStorage.setItem("user", JSON.stringify(userData));
  };

  // В AuthContext.js
  const logout = () => {
    setUser(null); // Сбросим данные в контексте
    localStorage.removeItem('user'); // Удаляем данные пользователя из localStorage
  };



  return (
    <AuthContext.Provider value={{ user, login, logout, setUser}}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
