<template>
  <nav class="dashboard">
    <router-link to="/dashboard" class="dashboard-link">Dashboard</router-link>
    <router-link to="/create-survey" class="dashboard-link">Create Survey</router-link>
   <router-link to="/survey-list" class="dashboard-link">Survey List</router-link>
    <router-link to="/ahploader" class="dashboard-link">AHP Loader</router-link>
  </nav>
</template>

<script>
export default {
  name: 'DashboardComponent'
};
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  padding: 10px;
  background-color: #f8f9fa;
  border-bottom: 1px solid #ddd;
}

.dashboard-link {
  padding: 10px 15px;
  text-decoration: none;
  color: #007bff;
  border: 1px solid #007bff;
  border-radius: 4px;
  transition: background-color 0.3s, color 0.3s;
}

.dashboard-link:hover {
  background-color: #007bff;
  color: #fff;
}
</style>
