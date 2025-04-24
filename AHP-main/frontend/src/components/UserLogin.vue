<template>
  <div>
    <input type="text" v-model="user" placeholder="User" /><br>
    <input type="password" v-model="password" placeholder="Password" /><br>
    <button @click="login">Login</button>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      user: '',
      password: '',
    };
  },
  methods: {
    async login() {
      try {
        const response = await axios.post('/api/login', {
          username: this.user,
          password: this.password,
        });

        if (response.data && response.data.token) {
          localStorage.token = response.data.token
          localStorage.userRole = response.data.role
          this.$router.push('/dashboard')
        } else {
          alert('Invalid login or password!')
        }
      } catch (error) {
        console.error('Login error:', error)
        alert('Login failed. Please check your credentials.')
      }
    },
  },
};
</script>

<style>
input, select, button {
  margin-bottom: 15px;
  padding: 10px;
  font-size: 16px;
  width: 200px;
  text-align: center;
}
.config-container {
  border: 2px solid #ccc;
  padding: 20px;
  margin-bottom: 20px;
}
.error-message {
  color: red;
  font-weight: bold;
}
button {
  width: 220px;
}
</style>
