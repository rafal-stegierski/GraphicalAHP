<template>
  <div>
    <DashboardComponent />
    <div class="main-content">
      <router-view />
    </div>
  </div>
</template>

<script>
import DashboardComponent from './DashboardComponent.vue';

export default {
  name: 'MainLayout',
  components: {
    DashboardComponent
  }
};
</script>

<style scoped>
.main-content {
  padding: 20px;
}
</style>
