<template>
  <div class="dashboard">
    <h1>Dashboard</h1>
    <button @click="goToRoute('/create-survey')">Create a new survey</button>
    <button @click="goToRoute('/ahploader')">Fill an existing survey</button>
    <button @click="goToRoute('/survey-list')">List of surveys</button>
  </div>
</template>

<script>
export default {
  methods: {
    goToRoute(route) {
      this.$router.push(route);
    }
  }
}
</script>

<style>
button {
  margin: 10px;
  padding: 10px;
}
</style>
