<template>

    <div id="app">
        <router-view />
    </div>
  </template>

<script>

export default {
  name: 'App',
  components: {
  }
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  min-height: 100vh;
  display: flex;
  /* align-items: center; */
  height: 100%;
  width: 100%; /* 添加这行 */
  background-color: #f4e3cc1f;
}


</style>
