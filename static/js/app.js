	Vue.mixin({ delimiters: ['[[', ']]'] })
	
	new Vue({
    el: '#crearSesion',
    data: {
        numSec: '¡Hola desde Vue!',
        idCurso:''
    },
    mounted() {
        // Realizar la solicitud Ajax al cargar la página
        this.idCurso = document.getElementById('idCurso').value;
        this.makeRequest();
    },
    methods: {
        makeRequest: function () {
            // Realizar una solicitud AJAX utilizando Axios
            axios.get('/enumerarseciones/'+this.idCurso)
                .then(response => {
                    this.numSec = response.data.numSec;
                })
                .catch(error => {
                    console.error('Error en la solicitud AJAX', error);
                });
        }
    }
});
