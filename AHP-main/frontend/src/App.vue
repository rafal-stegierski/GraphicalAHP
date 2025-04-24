<template>
  <div id="app">
    <!-- Dynamiczny komponent na podstawie aktualnej ścieżki -->
    <router-view></router-view>
  </div>
</template>

<script>
export default {
  name: 'App',
  // Nie musisz już importować i rejestrować komponentów tutaj,
  // ponieważ są one teraz obsługiwane przez router
};
</script>

<style>
/* Jeśli chcesz zachować stylowanie, możesz je tutaj zostawić */
</style>


<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
