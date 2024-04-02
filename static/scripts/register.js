// Register page scripts

const goalSelect = document.getElementById('goal');
const bmrTypeSelect = document.getElementById('bmr_type');
const messageElement = document.getElementById('bmrMessage'); 

document.getElementById('advanced_details').style.display = 'none';

// Function to show/hide advanced details
document.getElementById('use_advanced_registration').addEventListener('change', function() {
    if(this.checked){
        document.getElementById('advanced_details').style.display = 'block';
    }
    else {
        document.getElementById('advanced_details').style.display = 'none';
    }
});

// Listen for changes in the goal select element
goalSelect.addEventListener('change', function() {
    // If the selected goal is "lose_weight"
    if (this.value === 'lose_weight') {
        // Set the BMR type to "mifflin_st_jeor"
        bmrTypeSelect.value = 'mifflin_st_jeor';
        // Disable the BMR type select element
        bmrTypeSelect.disabled = true;
        // Display a message to the user, innerHTML allows you to use HTML tags, single quotes or escaped double quotes are needed to escape the string
        messageElement.innerHTML = "Since your goal is to lose weight, we are using the <a href='https://reference.medscape.com/calculator/846/mifflin-st-jeor-equation'>Mifflin-St Jeor</a> formula to calculate your Basal Metabolic Rate (BMR). This formula is often considered most accurate for people who are trying to lose weight.";
    } else {
        // If the selected goal is not "lose_weight", enable the BMR type select element
        bmrTypeSelect.disabled = false;
        // Clear the message
        messageElement.textContent = '';
    }
});

let validationStates = {
    username: false,
    password: false,
    confirmPassword: false,
    age: false,
    gender: false
};

// CHANGE GOAL TIMEFRAMES
const goalTimeframes = {
    bulk: { casual: 12, determined: 6, very_determined: 3 },
    lose_weight: { casual: 10, determined: 5, very_determined: 2 },
    healthy_happiness: { casual: 12, determined: 12, very_determined: 12 },
    improve_posture: { casual: 8, determined: 4, very_determined: 2 },
    stress_reduction: { casual: 10, determined: 6, very_determined: 3 },
    improve_flexibility: { casual: 10, determined: 5, very_determined: 2 },
    improve_endurance: { casual: 8, determined: 4, very_determined: 2 },
    six_pack: { casual: 6, determined: 3, very_determined: 1 },
};

//Function to update body fat input, if needed
document.getElementById('bmr_type').addEventListener('change', function() {
    var bfInput = document.getElementById('body_fat_percentage');
    var bfLabel = document.getElementById('bf_label');
    
    if(this.value == 'katch_mcardle') {
        bfInput.style.display = 'block';
        bfLabel.style.display = 'block';
    } else {
        bfInput.style.display = 'none';
        bfLabel.style.display = 'none';
    }
});

// changeGoalTimeframe() is called when the goal or determination level is changed
function changeGoalTimeframe() {
    const goal = document.getElementById('goal').value;
    const determination = document.getElementById('determination_level').value;
    const timeframe = goalTimeframes[goal] ? goalTimeframes[goal][determination] : null;
    
    if (timeframe) {
        const goalTimeframe = document.getElementById('goal_timeframe');
        const goalTimeframeDisplay = document.getElementById('goal_timeframe-display');
        
        goalTimeframe.value = timeframe;
        goalTimeframeDisplay.textContent = `Estimated timeframe: ${timeframe} months`;
    }
}


function handleGenderSelect(selectElement) {
    let genderTooltip = document.getElementById("genderTooltip");

    if (selectElement.value === 'other') {
        genderTooltip.style.display = "inline-block";
        genderTooltip.innerHTML = "Gender plays a crucial role in the calculation of daily calorie needs, as it influences factors such as basal metabolic rate, muscle mass, and energy expenditure. Therefore, it is necessary to provide your biological gender for a more accurate determination of your personalised calorie count.";
        selectElement.value = ''; // reset the select to the placeholder
        validationStates.gender = false;
    } else {
        genderTooltip.style.display = "none";
        validationStates.gender = true;
    }
    updateButtonState();
}


const changeHeightInput = () => {
    let unit = document.getElementById("height_unit").value;
    let input_div = document.getElementById("height_input");

    if (unit == "cm") {
        input_div.innerHTML = '<input type="number" id="height_cm" name="height_cm" min="1" required>';
    } else if (unit == "ft") {  
        input_div.innerHTML = '<input type="number" id="height_ft" name="height_ft" min="1" max="8" required>ft' +
                              '<input type="number" id="height_in" name="height_in" min="0" max="11" required>in';
    }
    else {
        console.log("Error: Invalid unit");
    }
}

// Check registration
document.addEventListener("DOMContentLoaded", () => {
    const usernameInput = document.getElementById("username");
    const passwordInput = document.getElementById("password");
    const confirmPasswordInput = document.getElementById("confirm-password");
    const usernameError = document.getElementById("username-error");
    //const passwordError = document.getElementById("password-error");
    const confirmPasswordError = document.getElementById("confirm-password-error");
    //const registerBtns = document.querySelectorAll(".reg_log_submit_btns");
    const ageInput = document.getElementById("age");
    const genderSelect = document.getElementById("gender");

    let debounceTimer;

    function checkAllValidationStates() {
        // Check if all validationStates values are true
        const allValid = Object.values(validationStates).every(state => state === true);
        
        if (allValid) {
            // If all validations are passed, you could enable the register button or alert the user
            // This is a simple alert for demonstration; you might want to handle this differently
            alert("All validations are passed. You can now submit the form.");
        } else {
            // If not all validations are passed, alert or handle accordingly
            alert("Some validations are not passed. Please check your inputs.");
        }
    }


    genderSelect.addEventListener("change", () => {
        handleGenderSelect(genderSelect);
    });

    usernameInput.addEventListener("input", () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            const username = usernameInput.value.trim();
            if (username !== "") {
                checkUsernameAvailability(username);
            }
        }, 500);
    });

    passwordInput.addEventListener("input", () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            const password = passwordInput.value.trim();
            if (password !== "") {
                checkPasswordFormat(password);
            }
        }, 500);
    });

    confirmPasswordInput.addEventListener("input", () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            const password = passwordInput.value.trim();
            const confirmPassword = confirmPasswordInput.value.trim();
            if (confirmPassword !== "") {
                checkPasswordConfirmation(password, confirmPassword);
            }
        }, 500);
    });

    ageInput.addEventListener("input", () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            if (ageInput.value !== ""){
                checkAge();
            }
        }, 500);
    });

    function checkPasswordFormat(password) {
        let passwordError = document.getElementById("password-error");
        let passwordInput = document.getElementById("password");
    
        // Check for different character types
        const hasLowercase = /[a-z]/.test(password);
        const hasUppercase = /[A-Z]/.test(password);
        const hasDigits = /\d/.test(password);
        const hasSpecial = /[!@#$%^&*()_\-+=\[\]{};:\\|,.<>\/?]/.test(password);
    
        let strength = 0;

        // Check for minimum length
        const hasMinLength = password.length >= 8;

        if (!hasMinLength) {
            passwordInput.style.backgroundColor = "#FF0000"; // Red: Too short
            passwordError.textContent = "Password is too short, 8 miniumum characters required";
            passwordError.style.fontWeight = "bold";
            validationStates.password = false;
        } else {
            passwordInput.style.backgroundColor = '';
            passwordError.textContent = "";
            validationStates.password = true;
        }
    
        if (hasLowercase && hasDigits && password) strength++;
        if (hasLowercase && hasUppercase && hasDigits) strength++;
        if (hasLowercase && hasUppercase && hasDigits && hasSpecial) strength++;
    
        switch (strength) {
            case 0:
                passwordInput.style.backgroundColor = "#FF0000"; // Red: Weak password
                break;
            case 1:
                passwordInput.style.backgroundColor = "#FFFF00"; // Yellow: Ok password
                break;
            case 2:
                passwordInput.style.backgroundColor = "#9ACD32"; // Yellow Green: Good password
                break;
            case 3:
                passwordInput.style.backgroundColor = "#008000"; // Green: Very Strong password
                break;
        }
    
        // Update validationStates and button state
        validationStates.password = strength >= 1;
        updateButtonState();
    }

    function checkPasswordConfirmation(password, confirmPassword) {
        if (password !== confirmPassword) {
            confirmPasswordError.textContent = "Passwords do not match";
            confirmPasswordError.style.fontWeight = "bold";
            validationStates.confirmPassword = false;
        } else {
            confirmPasswordError.textContent = "";
            validationStates.confirmPassword = true;
        }

        // Update validationStates and button state
        updateButtonState();
    }

    function checkUsernameAvailability(username) {
        // Show loading indicator
        usernameError.textContent = "";
        
        fetch("/check-username", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ username }),
        })
        .then((response) => response.json())
        .then((data) => {
            if (data.available) {
                // Username is available
                usernameError.textContent = "";
                validationStates.username = true;
            } else {
                // Username is already taken
                usernameError.textContent = "Username is already taken";
                validationStates.username = false;
            }

            // Update validationStates and button state
            updateButtonState();
        })
        .catch((error) => {
            console.error("Error checking username availability:", error);
        });
    }

    const checkAge = () => {
        let age = +ageInput.value;
        let ageError = document.getElementById("age_error");

        if (age <= 0 || age > 120) {
            ageError.innerHTML = "Age must be between 1 and 120";
            ageError.style.fontWeight = "bold";
            validationStates.age = false;
        } else {
            ageError.textContent = "";
            validationStates.age = true;
        }

        // Update validationStates and button state
        updateButtonState();
    }
});
